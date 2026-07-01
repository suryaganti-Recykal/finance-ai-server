import uuid
from datetime import datetime
from decimal import Decimal

from src.domain.marketing.entities.metrics import Anomaly, CampaignMetrics, MarketingReport
from src.domain.marketing.repositories.marketing import MarketingRepository


class MarketingMetricsService:
    """Calculate marketing KPIs, detect anomalies, and generate reports."""

    def __init__(self, marketing_repo: MarketingRepository) -> None:
        self.repo = marketing_repo

    async def calculate_campaign_metrics(
        self,
        company_id: uuid.UUID,
        campaign_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> CampaignMetrics | None:
        """Calculate all KPIs for a single campaign."""
        metrics = await self.repo.get_campaign_metrics(company_id, campaign_id, start_date, end_date)
        if not metrics:
            return None

        # Calculate derived metrics
        metrics.cpl = (metrics.total_spend / metrics.leads) if metrics.leads > 0 else Decimal(0)
        metrics.cpp = (
            (metrics.total_spend / metrics.purchases) if metrics.purchases > 0 else None
        )
        metrics.cpc = (
            (metrics.total_spend / metrics.clicks) if metrics.clicks > 0 else Decimal(0)
        )
        metrics.ctr = (
            (Decimal(metrics.clicks) / metrics.impressions * 100)
            if metrics.impressions > 0
            else Decimal(0)
        )

        # Get previous period for comparison
        prev_metrics = await self.repo.get_previous_period_metrics(
            company_id, campaign_id, start_date, end_date
        )
        if prev_metrics:
            metrics.spend_change_percent = self._percent_change(prev_metrics.total_spend, metrics.total_spend)
            metrics.leads_change_percent = self._percent_change(prev_metrics.leads, metrics.leads)
            prev_cpl = (prev_metrics.total_spend / prev_metrics.leads) if prev_metrics.leads > 0 else Decimal(0)
            metrics.cpl_change_percent = self._percent_change(prev_cpl, metrics.cpl)

        return metrics

    async def generate_report(
        self,
        company_id: uuid.UUID,
        start_date: datetime,
        end_date: datetime,
    ) -> MarketingReport:
        """Generate a full marketing report with all campaigns and anomalies."""
        campaigns = await self.repo.get_campaigns_in_period(company_id, start_date, end_date)

        # Calculate overall metrics
        total_spend = await self.repo.get_total_marketing_spend(company_id, start_date, end_date)
        total_leads, total_purchases = await self.repo.get_total_conversions(
            company_id, start_date, end_date
        )
        total_impressions = sum(c.impressions for c in campaigns)
        total_clicks = sum(c.clicks for c in campaigns)

        overall_cpl = (total_spend / total_leads) if total_leads > 0 else Decimal(0)
        overall_cpp = (total_spend / total_purchases) if total_purchases > 0 else None
        overall_ctr = (
            (Decimal(total_clicks) / total_impressions * 100)
            if total_impressions > 0
            else Decimal(0)
        )

        # Detect anomalies
        anomalies = await self._detect_anomalies(
            company_id, campaigns, start_date, end_date
        )

        return MarketingReport(
            period_start=start_date,
            period_end=end_date,
            total_spend=total_spend,
            total_leads=total_leads,
            total_purchases=total_purchases,
            total_impressions=total_impressions,
            total_clicks=total_clicks,
            overall_cpl=overall_cpl,
            overall_cpp=overall_cpp,
            overall_ctr=overall_ctr,
            campaigns=campaigns,
            anomalies=anomalies,
        )

    async def _detect_anomalies(
        self,
        company_id: uuid.UUID,
        campaigns: list[CampaignMetrics],
        start_date: datetime,
        end_date: datetime,
    ) -> list[Anomaly]:
        """Detect unusual patterns: high spend, low conversion, high CPL, etc."""
        anomalies: list[Anomaly] = []

        for campaign in campaigns:
            # High spend spike (>50% increase)
            if campaign.spend_change_percent and campaign.spend_change_percent > Decimal(50):
                anomalies.append(
                    Anomaly(
                        anomaly_type="high_spend_spike",
                        severity="warning",
                        campaign_id=campaign.campaign_id,
                        campaign_name=campaign.campaign_name,
                        description=f"Spend increased by {campaign.spend_change_percent}% vs. previous period",
                        metric_name="total_spend",
                        expected_value=None,
                        actual_value=campaign.total_spend,
                        threshold=Decimal(150),  # 150% of previous
                        detected_at=datetime.utcnow(),
                    )
                )

            # Low conversion rate (<1 lead per 100 clicks)
            if campaign.clicks > 100:
                conversion_rate = Decimal(campaign.leads) / campaign.clicks * 100
                if conversion_rate < Decimal(1):
                    anomalies.append(
                        Anomaly(
                            anomaly_type="low_conversion_rate",
                            severity="warning",
                            campaign_id=campaign.campaign_id,
                            campaign_name=campaign.campaign_name,
                            description=f"Only {conversion_rate:.2f}% click-to-lead conversion",
                            metric_name="ctr",
                            expected_value=Decimal(1),
                            actual_value=conversion_rate,
                            threshold=Decimal(1),
                            detected_at=datetime.utcnow(),
                        )
                    )

            # High CPL (>2x median)
            # TODO: Calculate median CPL from all campaigns for comparison
            # For now, use threshold of $100
            if campaign.cpl > Decimal(100):
                anomalies.append(
                    Anomaly(
                        anomaly_type="high_cpl",
                        severity="info",
                        campaign_id=campaign.campaign_id,
                        campaign_name=campaign.campaign_name,
                        description=f"Cost per lead is ${campaign.cpl:.2f}",
                        metric_name="cpl",
                        expected_value=Decimal(50),
                        actual_value=campaign.cpl,
                        threshold=Decimal(100),
                        detected_at=datetime.utcnow(),
                    )
                )

        return anomalies

    @staticmethod
    def _percent_change(prev_value: Decimal | int, curr_value: Decimal | int) -> Decimal:
        """Calculate percent change from previous to current value."""
        prev = Decimal(prev_value) if isinstance(prev_value, int) else prev_value
        curr = Decimal(curr_value) if isinstance(curr_value, int) else curr_value

        if prev == 0:
            return Decimal(0) if curr == 0 else Decimal(100)

        return ((curr - prev) / prev * 100).quantize(Decimal("0.01"))
