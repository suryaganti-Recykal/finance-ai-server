from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class CampaignMetricsSchema(BaseModel):
    campaign_id: str
    campaign_name: str
    platform: str
    period: str
    period_start: datetime
    period_end: datetime
    total_spend: Decimal
    currency: str
    leads: int
    purchases: int
    impressions: int
    clicks: int
    cpl: Decimal
    cpp: Decimal | None
    cpc: Decimal
    ctr: Decimal
    roas: Decimal | None
    spend_change_percent: Decimal | None = None
    leads_change_percent: Decimal | None = None
    cpl_change_percent: Decimal | None = None


class AnomalySchema(BaseModel):
    anomaly_type: str
    severity: str
    campaign_id: str
    campaign_name: str
    description: str
    metric_name: str
    expected_value: Decimal | None
    actual_value: Decimal
    threshold: Decimal | None
    detected_at: datetime


class MarketingReportSchema(BaseModel):
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
    campaigns: list[CampaignMetricsSchema]
    anomalies: list[AnomalySchema]
