from datetime import datetime

from fastapi import APIRouter

from src.api.deps import CurrentCompanyId, DbSession
from src.application.marketing.use_cases.get_marketing_report import (
    GetMarketingReportInput,
    GetMarketingReportUseCase,
)
from src.infrastructure.db.repositories.marketing import MarketingRepositoryImpl
from src.schemas.common import SuccessResponse
from src.schemas.marketing import MarketingReportSchema

router = APIRouter(prefix="/marketing", tags=["Marketing"])


@router.get("", response_model=SuccessResponse[MarketingReportSchema])
async def get_marketing_report(
    company_id: CurrentCompanyId,
    db: DbSession,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> SuccessResponse[MarketingReportSchema]:
    """Get comprehensive marketing report with KPIs and anomalies for all campaigns."""
    repo = MarketingRepositoryImpl(db)
    use_case = GetMarketingReportUseCase(repo)

    report = await use_case.execute(
        GetMarketingReportInput(company_id=company_id, start_date=start_date, end_date=end_date)
    )

    # Convert entities to schema
    campaigns = [
        {
            "campaign_id": c.campaign_id,
            "campaign_name": c.campaign_name,
            "platform": c.platform,
            "period": c.period,
            "period_start": c.period_start,
            "period_end": c.period_end,
            "total_spend": c.total_spend,
            "currency": c.currency,
            "leads": c.leads,
            "purchases": c.purchases,
            "impressions": c.impressions,
            "clicks": c.clicks,
            "cpl": c.cpl,
            "cpp": c.cpp,
            "cpc": c.cpc,
            "ctr": c.ctr,
            "roas": c.roas,
            "spend_change_percent": c.spend_change_percent,
            "leads_change_percent": c.leads_change_percent,
            "cpl_change_percent": c.cpl_change_percent,
        }
        for c in report.campaigns
    ]

    anomalies = [
        {
            "anomaly_type": a.anomaly_type,
            "severity": a.severity,
            "campaign_id": a.campaign_id,
            "campaign_name": a.campaign_name,
            "description": a.description,
            "metric_name": a.metric_name,
            "expected_value": a.expected_value,
            "actual_value": a.actual_value,
            "threshold": a.threshold,
            "detected_at": a.detected_at,
        }
        for a in report.anomalies
    ]

    return SuccessResponse(
        data=MarketingReportSchema(
            period_start=report.period_start,
            period_end=report.period_end,
            total_spend=report.total_spend,
            total_leads=report.total_leads,
            total_purchases=report.total_purchases,
            total_impressions=report.total_impressions,
            total_clicks=report.total_clicks,
            overall_cpl=report.overall_cpl,
            overall_cpp=report.overall_cpp,
            overall_ctr=report.overall_ctr,
            campaigns=campaigns,
            anomalies=anomalies,
        )
    )
