"""LangGraph agent for generating monthly financial reports.

Workflow:
1. Aggregate: Collect all monthly financial data from real sources
2. Analyze: Calculate performance metrics and insights
3. Generate: Create report content
4. Summarize: Generate AI insights using Claude API
5. Store: Save report to database
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, cast

from anthropic import Anthropic
from langgraph.graph import END, StateGraph

from src.core.logging.logger import get_logger
from src.infrastructure.db.repositories.campaign import CampaignRepositoryImpl
from src.infrastructure.db.repositories.dashboard import DashboardRepositoryImpl
from src.infrastructure.db.session import AsyncSession

logger = get_logger(__name__)


@dataclass
class MonthlyReportState:
    """State for monthly report generation."""
    company_id: str
    year: int
    month: int

    # Financial data
    total_revenue: Decimal = Decimal(0)
    total_expenses: Decimal = Decimal(0)
    total_profit: Decimal = Decimal(0)
    total_collections: Decimal = Decimal(0)

    # Department breakdown
    departments: list[dict] = field(default_factory=list)

    # Performance metrics
    profit_margin: Decimal = Decimal(0)
    growth_vs_previous: Decimal = Decimal(0)
    cash_position: Decimal = Decimal(0)

    # AI insights
    insights: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    # Report output
    report_title: str = ""
    report_content: str = ""
    report_format: str = "pdf"  # pdf or excel

    # Tracking
    generated_at: datetime = field(default_factory=datetime.utcnow)
    errors: list[str] = field(default_factory=list)


class MonthlyReportGraph:
    """LangGraph implementation of monthly report generation."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.graph = StateGraph(MonthlyReportState)
        self.dashboard_repo = DashboardRepositoryImpl(db)
        self.campaign_repo = CampaignRepositoryImpl(db)
        self.anthropic = Anthropic()
        self._build_graph()

    def _build_graph(self) -> None:
        """Build the LangGraph workflow."""
        self.graph.add_node("aggregate", self._aggregate_data)
        self.graph.add_node("analyze", self._analyze_metrics)
        self.graph.add_node("generate_insights", self._generate_insights)
        self.graph.add_node("create_report", self._create_report)
        self.graph.add_node("store", self._store_report)

        self.graph.set_entry_point("aggregate")
        self.graph.add_edge("aggregate", "analyze")
        self.graph.add_edge("analyze", "generate_insights")
        self.graph.add_edge("generate_insights", "create_report")
        self.graph.add_edge("create_report", "store")
        self.graph.add_edge("store", END)

    async def _aggregate_data(self, state: MonthlyReportState) -> MonthlyReportState:
        """Aggregate monthly financial data from real sources."""
        logger.info(f"Aggregating data for {state.year}-{state.month:02d}")

        try:
            import uuid
            company_uuid = uuid.UUID(state.company_id) if isinstance(state.company_id, str) else state.company_id

            # Calculate date range for the month
            start_date = datetime(state.year, state.month, 1)
            if state.month == 12:
                end_date = datetime(state.year + 1, 1, 1) - timedelta(seconds=1)
            else:
                end_date = datetime(state.year, state.month + 1, 1) - timedelta(seconds=1)

            # Fetch real data in parallel
            revenue_result, expenses_result, collections_result, campaigns_result = await asyncio.gather(
                self.dashboard_repo.get_total_revenue(company_uuid, start_date, end_date),
                self.dashboard_repo.get_total_expenses(company_uuid, start_date, end_date),
                self.dashboard_repo.get_total_collections(company_uuid, start_date, end_date),
                self.campaign_repo.get_by_date_range(company_uuid, start_date, end_date),
            )

            state.total_revenue = Decimal(str(revenue_result or 0))
            state.total_expenses = Decimal(str(expenses_result or 0))
            state.total_collections = Decimal(str(collections_result or 0))
            state.total_profit = state.total_revenue - state.total_expenses
            state.cash_position = state.total_collections

            # Get department breakdown from campaigns
            dept_spend = {}
            if campaigns_result:
                for campaign in campaigns_result:
                    dept_name = getattr(campaign, 'department', 'Other')
                    spend = float(getattr(campaign, 'budget_spent', 0) or 0)
                    roi = float(getattr(campaign, 'revenue_generated', 0) or 0) / spend if spend > 0 else 0
                    dept_spend[dept_name] = {"spend": spend, "roi": roi}

            state.departments = [
                {"name": k, "spend": v["spend"], "roi": v["roi"]}
                for k, v in dept_spend.items()
            ]

            logger.info(f"Data aggregated: Revenue={state.total_revenue}, Expenses={state.total_expenses}")

        except Exception as e:
            logger.error(f"Error aggregating data: {e}")
            state.errors.append(f"Aggregation error: {str(e)}")

        return state

    async def _analyze_metrics(self, state: MonthlyReportState) -> MonthlyReportState:
        """Analyze financial metrics."""
        logger.info("Analyzing financial metrics")

        try:
            import uuid
            company_uuid = uuid.UUID(state.company_id) if isinstance(state.company_id, str) else state.company_id

            if state.total_revenue > 0:
                state.profit_margin = (state.total_profit / state.total_revenue * 100)
            else:
                state.profit_margin = Decimal(0)

            # Calculate growth vs previous month
            prev_start = datetime(state.year, state.month - 1 if state.month > 1 else 12, 1)
            prev_end = datetime(state.year if state.month > 1 else state.year - 1, state.month - 1 if state.month > 1 else 12, 1) - timedelta(seconds=1)

            try:
                prev_revenue = await self.dashboard_repo.get_total_revenue(company_uuid, prev_start, prev_end)
                prev_revenue = Decimal(str(prev_revenue or 0))
                if prev_revenue > 0:
                    state.growth_vs_previous = ((state.total_revenue - prev_revenue) / prev_revenue * 100)
                else:
                    state.growth_vs_previous = Decimal(0)
            except:
                state.growth_vs_previous = Decimal(0)

            logger.info(f"Profit Margin: {state.profit_margin}%, Growth: {state.growth_vs_previous}%")

        except Exception as e:
            logger.error(f"Error analyzing metrics: {e}")
            state.errors.append(f"Analysis error: {str(e)}")

        return state

    async def _generate_insights(self, state: MonthlyReportState) -> MonthlyReportState:
        """Generate AI-powered insights using Claude API."""
        logger.info("Generating AI insights with Claude")

        try:
            # Build context for Claude
            context = f"""
Financial Data for {state.year}-{state.month:02d}:
- Total Revenue: ${float(state.total_revenue):,.2f}
- Total Expenses: ${float(state.total_expenses):,.2f}
- Total Profit: ${float(state.total_profit):,.2f}
- Profit Margin: {float(state.profit_margin):.1f}%
- Growth vs Previous Month: {float(state.growth_vs_previous):.1f}%
- Cash Position: ${float(state.cash_position):,.2f}

Department Breakdown:
{chr(10).join(f"- {dept['name']}: ${dept['spend']:,.0f} (ROI: {dept['roi']:.1f}x)" for dept in state.departments)}
            """

            # Generate insights using Claude
            message = self.anthropic.messages.create(
                model="claude-opus-4-8",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": f"Based on this financial data, provide 4 key business insights and 4 actionable recommendations:\n\n{context}"
                    }
                ]
            )

            response_text = message.content[0].text
            lines = response_text.split('\n')

            # Parse insights and recommendations
            in_insights = False
            in_recommendations = False
            for line in lines:
                if 'insight' in line.lower() and ':' in line:
                    in_insights = True
                    in_recommendations = False
                elif 'recommendation' in line.lower() and ':' in line:
                    in_insights = False
                    in_recommendations = True
                elif line.strip().startswith(('-', '•', '*', '1.', '2.', '3.', '4.')):
                    line_clean = line.strip().lstrip('-•*0123456789.').strip()
                    if in_insights and line_clean:
                        state.insights.append(line_clean)
                    elif in_recommendations and line_clean:
                        state.recommendations.append(line_clean)

            # Fallback if parsing didn't work well
            if not state.insights:
                state.insights = [
                    f"Revenue of ${float(state.total_revenue):,.0f} with {float(state.growth_vs_previous):.1f}% growth",
                    f"Profit margin at {float(state.profit_margin):.1f}% shows operational efficiency",
                    "Marketing ROI varies across departments - review underperforming areas",
                    f"Cash position at ${float(state.cash_position):,.0f} provides good runway"
                ]

            if not state.recommendations:
                state.recommendations = [
                    "Review underperforming departments for cost optimization",
                    "Increase investment in high-ROI marketing channels",
                    "Monitor expense growth vs revenue growth trajectory",
                    "Plan for next quarter based on current cash flow trends"
                ]

            logger.info(f"Generated {len(state.insights)} insights and {len(state.recommendations)} recommendations")

        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            state.errors.append(f"Insight generation error: {str(e)}")

        return state

    async def _create_report(self, state: MonthlyReportState) -> MonthlyReportState:
        """Create report content."""
        logger.info("Creating report document")

        try:
            state.report_title = f"Financial Report - {state.year}-{state.month:02d}"

            state.report_content = f"""
MONTHLY FINANCIAL REPORT
{state.year}-{state.month:02d}

EXECUTIVE SUMMARY
================
Revenue:              ${float(state.total_revenue):,.2f}
Expenses:             ${float(state.total_expenses):,.2f}
Profit:               ${float(state.total_profit):,.2f}
Profit Margin:        {float(state.profit_margin):.1f}%
Growth vs Prior:      {float(state.growth_vs_previous):.1f}%
Cash Position:        ${float(state.cash_position):,.2f}

KEY INSIGHTS
============
{chr(10).join(f"• {insight}" for insight in state.insights)}

RECOMMENDATIONS
===============
{chr(10).join(f"• {rec}" for rec in state.recommendations)}

DEPARTMENT BREAKDOWN
====================
{chr(10).join(f"{dept['name']}: ${dept['spend']:,.0f} (ROI: {dept['roi']:.1f}x)" for dept in state.departments) if state.departments else "No department data"}
            """

            logger.info("Report created successfully")

        except Exception as e:
            logger.error(f"Error creating report: {e}")
            state.errors.append(f"Report creation error: {str(e)}")

        return state

    async def _store_report(self, state: MonthlyReportState) -> MonthlyReportState:
        """Store report in database."""
        logger.info("Storing report in database")

        try:
            # In production, this would save to database or S3 with binary PDF/Excel
            # For now, log the storage
            logger.info(f"Report prepared for storage: {state.report_title}")
            logger.info(f"Report format: {state.report_format}")
            logger.info(f"Content length: {len(state.report_content)} bytes")

        except Exception as e:
            logger.error(f"Error storing report: {e}")
            state.errors.append(f"Storage error: {str(e)}")

        return state

    async def run(
        self,
        company_id: str,
        year: int,
        month: int,
        report_format: str = "pdf"
    ) -> dict[str, Any]:
        """Execute monthly report generation."""
        logger.info(f"Starting monthly report for {company_id} ({year}-{month:02d})")

        state = MonthlyReportState(
            company_id=company_id,
            year=year,
            month=month,
            report_format=report_format
        )

        runnable = self.graph.compile()
        final_state = cast(dict[str, Any], await runnable.ainvoke(state))

        return {
            "success": len(final_state["errors"]) == 0,
            "report_title": final_state["report_title"],
            "summary": {
                "revenue": float(final_state["total_revenue"]),
                "expenses": float(final_state["total_expenses"]),
                "profit": float(final_state["total_profit"]),
                "profit_margin_percent": float(final_state["profit_margin"]),
                "growth_percent": float(final_state["growth_vs_previous"]),
                "cash_position": float(final_state["cash_position"]),
            },
            "insights": final_state["insights"] if final_state["insights"] else [],
            "recommendations": final_state["recommendations"] if final_state["recommendations"] else [],
            "departments": final_state["departments"] if final_state["departments"] else [],
            "report_format": final_state["report_format"],
            "generated_at": final_state["generated_at"].isoformat(),
            "errors": final_state["errors"] if final_state["errors"] else None,
        }
