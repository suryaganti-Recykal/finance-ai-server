"""LangGraph agent for marketing spend analysis and anomaly detection.

Workflow:
1. Fetch: Get campaign data from database
2. Calculate: Compute KPIs (CPL, CPP, ROAS, CTR, conversion rate)
3. Detect: Find anomalies vs historical averages
4. Report: Aggregate and return results
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

from langgraph.graph import StateGraph, END

from src.core.logging.logger import get_logger
from src.infrastructure.db.repositories.marketing import MarketingRepositoryImpl
from src.infrastructure.db.repositories.campaign import CampaignRepositoryImpl
from src.infrastructure.db.session import AsyncSession

logger = get_logger(__name__)


@dataclass
class CampaignMetrics:
    """Metrics for a single campaign."""
    campaign_id: str
    campaign_name: str
    spend: Decimal
    impressions: int
    clicks: int
    conversions: int
    revenue: Decimal

    # Calculated KPIs
    cpl: Decimal = Decimal(0)  # Cost per lead
    cpp: Decimal = Decimal(0)  # Cost per impression
    cpc: Decimal = Decimal(0)  # Cost per click
    ctr: Decimal = Decimal(0)  # Click-through rate (%)
    conversion_rate: Decimal = Decimal(0)  # Conversions / clicks (%)
    roas: Decimal = Decimal(0)  # Return on ad spend


@dataclass
class Anomaly:
    """Detected anomaly in campaign performance."""
    campaign_id: str
    campaign_name: str
    metric: str
    current_value: Decimal
    expected_value: Decimal
    variance: Decimal  # As percentage
    type: str  # "positive" or "negative"


@dataclass
class MarketingState:
    """State for marketing analysis workflow."""
    company_id: str
    time_period_days: int = 30

    # Intermediate results
    campaigns: list[Any] = field(default_factory=list)
    campaign_metrics: list[CampaignMetrics] = field(default_factory=list)
    anomalies: list[Anomaly] = field(default_factory=list)

    # Aggregates
    total_spend: Decimal = Decimal(0)
    total_revenue: Decimal = Decimal(0)
    overall_roas: Decimal = Decimal(0)
    best_campaign: str = ""
    worst_campaign: str = ""

    # Tracking
    errors: list[str] = field(default_factory=list)


class MarketingSpendGraph:
    """LangGraph implementation of marketing spend analysis."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.graph = StateGraph(MarketingState)
        self.marketing_repo = MarketingRepositoryImpl(db)
        self.campaign_repo = CampaignRepositoryImpl(db)
        self._build_graph()

    def _build_graph(self) -> None:
        """Build the LangGraph workflow."""
        self.graph.add_node("fetch", self._fetch_campaigns)
        self.graph.add_node("calculate", self._calculate_metrics)
        self.graph.add_node("detect_anomalies", self._detect_anomalies)
        self.graph.add_node("aggregate", self._aggregate)
        self.graph.add_node("report", self._report)

        self.graph.set_entry_point("fetch")
        self.graph.add_edge("fetch", "calculate")
        self.graph.add_edge("calculate", "detect_anomalies")
        self.graph.add_edge("detect_anomalies", "aggregate")
        self.graph.add_edge("aggregate", "report")
        self.graph.add_edge("report", END)

    async def _fetch_campaigns(self, state: MarketingState) -> MarketingState:
        """Fetch campaign data from database."""
        logger.info(f"Fetching campaigns for {state.company_id}")

        try:
            # Get all campaigns for company in last N days
            cutoff_date = datetime.utcnow() - timedelta(days=state.time_period_days)
            campaigns = await self.marketing_repo.get_campaigns_by_date_range(
                state.company_id,
                cutoff_date,
                datetime.utcnow()
            )

            state.campaigns = campaigns
            logger.info(f"Fetched {len(campaigns)} campaigns")

        except Exception as e:
            logger.error(f"Error fetching campaigns: {e}")
            state.errors.append(f"Fetch error: {str(e)}")

        return state

    async def _calculate_metrics(self, state: MarketingState) -> MarketingState:
        """Calculate KPIs for each campaign."""
        logger.info("Calculating metrics")

        for campaign in state.campaigns:
            try:
                spend = Decimal(str(campaign.budget_spent or 0))
                impressions = campaign.impressions or 0
                clicks = campaign.clicks or 0
                conversions = campaign.conversions or 0
                revenue = Decimal(str(campaign.revenue_generated or 0))

                # Calculate KPIs
                cpl = spend / conversions if conversions > 0 else Decimal(0)
                cpp = spend / impressions if impressions > 0 else Decimal(0)
                cpc = spend / clicks if clicks > 0 else Decimal(0)
                ctr = (clicks / impressions * 100) if impressions > 0 else Decimal(0)
                conversion_rate = (conversions / clicks * 100) if clicks > 0 else Decimal(0)
                roas = revenue / spend if spend > 0 else Decimal(0)

                metrics = CampaignMetrics(
                    campaign_id=str(campaign.id),
                    campaign_name=campaign.name,
                    spend=spend,
                    impressions=impressions,
                    clicks=clicks,
                    conversions=conversions,
                    revenue=revenue,
                    cpl=cpl,
                    cpp=cpp,
                    cpc=cpc,
                    ctr=ctr,
                    conversion_rate=conversion_rate,
                    roas=roas,
                )

                state.campaign_metrics.append(metrics)

            except Exception as e:
                logger.error(f"Error calculating metrics for {campaign.name}: {e}")
                state.errors.append(f"Metric calculation error: {str(e)}")

        logger.info(f"Calculated metrics for {len(state.campaign_metrics)} campaigns")
        return state

    async def _detect_anomalies(self, state: MarketingState) -> MarketingState:
        """Detect anomalies in campaign performance."""
        logger.info("Detecting anomalies")

        if len(state.campaign_metrics) < 2:
            logger.info("Not enough campaigns for anomaly detection")
            return state

        # Calculate averages
        avg_roas = sum(c.roas for c in state.campaign_metrics) / len(state.campaign_metrics)
        avg_ctr = sum(c.ctr for c in state.campaign_metrics) / len(state.campaign_metrics)
        avg_conversion_rate = sum(c.conversion_rate for c in state.campaign_metrics) / len(state.campaign_metrics)
        avg_cpc = sum(c.cpc for c in state.campaign_metrics) / len(state.campaign_metrics)

        for campaign in state.campaign_metrics:
            # Check ROAS variance
            if avg_roas > 0:
                roas_variance = abs(campaign.roas - avg_roas) / avg_roas * 100
                if roas_variance > 20:
                    state.anomalies.append(Anomaly(
                        campaign_id=campaign.campaign_id,
                        campaign_name=campaign.campaign_name,
                        metric="ROAS",
                        current_value=campaign.roas,
                        expected_value=avg_roas,
                        variance=Decimal(str(roas_variance)),
                        type="positive" if campaign.roas > avg_roas else "negative"
                    ))

            # Check CTR variance
            if avg_ctr > 0:
                ctr_variance = abs(campaign.ctr - avg_ctr) / avg_ctr * 100
                if ctr_variance > 20:
                    state.anomalies.append(Anomaly(
                        campaign_id=campaign.campaign_id,
                        campaign_name=campaign.campaign_name,
                        metric="CTR",
                        current_value=campaign.ctr,
                        expected_value=avg_ctr,
                        variance=Decimal(str(ctr_variance)),
                        type="positive" if campaign.ctr > avg_ctr else "negative"
                    ))

            # Check CPC variance
            if avg_cpc > 0:
                cpc_variance = abs(campaign.cpc - avg_cpc) / avg_cpc * 100
                if cpc_variance > 20:
                    state.anomalies.append(Anomaly(
                        campaign_id=campaign.campaign_id,
                        campaign_name=campaign.campaign_name,
                        metric="CPC",
                        current_value=campaign.cpc,
                        expected_value=avg_cpc,
                        variance=Decimal(str(cpc_variance)),
                        type="negative" if campaign.cpc > avg_cpc else "positive"
                    ))

        logger.info(f"Detected {len(state.anomalies)} anomalies")
        return state

    async def _aggregate(self, state: MarketingState) -> MarketingState:
        """Aggregate metrics across all campaigns."""
        logger.info("Aggregating metrics")

        if not state.campaign_metrics:
            logger.warning("No campaigns to aggregate")
            return state

        state.total_spend = sum(c.spend for c in state.campaign_metrics)
        state.total_revenue = sum(c.revenue for c in state.campaign_metrics)

        if state.total_spend > 0:
            state.overall_roas = state.total_revenue / state.total_spend
        else:
            state.overall_roas = Decimal(0)

        # Find best and worst
        if state.campaign_metrics:
            best = max(state.campaign_metrics, key=lambda c: c.roas)
            worst = min(state.campaign_metrics, key=lambda c: c.roas)
            state.best_campaign = best.campaign_name
            state.worst_campaign = worst.campaign_name

        logger.info(f"Total spend: {state.total_spend}, Overall ROAS: {state.overall_roas}")
        return state

    async def _report(self, state: MarketingState) -> MarketingState:
        """Generate final report."""
        logger.info("Generating marketing report")
        logger.info(f"""
Marketing Report:
  Campaigns: {len(state.campaign_metrics)}
  Total Spend: ${state.total_spend}
  Total Revenue: ${state.total_revenue}
  Overall ROAS: {state.overall_roas}x
  Best: {state.best_campaign}
  Worst: {state.worst_campaign}
  Anomalies: {len(state.anomalies)}
        """)
        return state

    async def run(self, company_id: str, time_period_days: int = 30) -> dict[str, Any]:
        """Execute the marketing spend analysis."""
        logger.info(f"Starting marketing analysis for {company_id}")

        state = MarketingState(
            company_id=company_id,
            time_period_days=time_period_days
        )

        runnable = self.graph.compile()
        final_state = await runnable.ainvoke(state)

        return {
            "success": len(final_state.errors) == 0,
            "total_spend": float(final_state.total_spend),
            "total_revenue": float(final_state.total_revenue),
            "overall_roas": float(final_state.overall_roas),
            "campaigns": [
                {
                    "campaign_id": c.campaign_id,
                    "campaign_name": c.campaign_name,
                    "spend": float(c.spend),
                    "impressions": c.impressions,
                    "clicks": c.clicks,
                    "conversions": c.conversions,
                    "revenue": float(c.revenue),
                    "kpis": {
                        "cpl": float(c.cpl),
                        "cpp": float(c.cpp),
                        "cpc": float(c.cpc),
                        "ctr": float(c.ctr),
                        "conversion_rate": float(c.conversion_rate),
                        "roas": float(c.roas),
                    }
                }
                for c in final_state.campaign_metrics
            ],
            "anomalies": [
                {
                    "campaign_name": a.campaign_name,
                    "metric": a.metric,
                    "current_value": float(a.current_value),
                    "expected_value": float(a.expected_value),
                    "variance": float(a.variance),
                    "type": a.type,
                }
                for a in final_state.anomalies
            ],
            "best_campaign": final_state.best_campaign,
            "worst_campaign": final_state.worst_campaign,
            "errors": final_state.errors if final_state.errors else None,
        }
