from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(kw_only=True)
class CampaignMetrics:
    """Calculated KPIs for a single campaign."""

    campaign_id: str
    campaign_name: str
    platform: str
    period: str  # "daily", "weekly", "monthly"
    period_start: datetime
    period_end: datetime

    total_spend: Decimal
    currency: str
    leads: int
    purchases: int
    impressions: int
    clicks: int

    # Calculated metrics
    cpl: Decimal  # Cost Per Lead = spend / leads
    cpp: Decimal | None  # Cost Per Purchase = spend / purchases
    cpc: Decimal  # Cost Per Click = spend / clicks
    ctr: Decimal  # Click-Through Rate = clicks / impressions * 100
    roas: Decimal | None  # Return On Ad Spend (requires revenue mapping, placeholder)

    # Change metrics (vs. previous period)
    spend_change_percent: Decimal | None = None
    leads_change_percent: Decimal | None = None
    cpl_change_percent: Decimal | None = None


@dataclass(kw_only=True)
class Anomaly:
    """Flagged unusual pattern in marketing data."""

    anomaly_type: str  # "high_spend", "low_conversion", "high_cpl", "ctr_drop", etc.
    severity: str  # "info", "warning", "critical"
    campaign_id: str
    campaign_name: str
    description: str
    metric_name: str
    expected_value: Decimal | None
    actual_value: Decimal
    threshold: Decimal | None
    detected_at: datetime


@dataclass(kw_only=True)
class MarketingReport:
    """Full marketing spend report for a period."""

    period_start: datetime
    period_end: datetime
    total_spend: Decimal
    total_leads: int
    total_purchases: int
    total_impressions: int
    total_clicks: int
    overall_cpl: Decimal
    overall_cpp: Decimal | None
    overall_ctr: Decimal
    campaigns: list[CampaignMetrics]
    anomalies: list[Anomaly]
