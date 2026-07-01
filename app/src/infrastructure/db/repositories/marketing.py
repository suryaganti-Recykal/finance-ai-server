import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.marketing.entities.metrics import CampaignMetrics
from src.domain.marketing.repositories.marketing import MarketingRepository
from src.infrastructure.db.models.campaign import CampaignModel


class MarketingRepositoryImpl(MarketingRepository):
    """SQLAlchemy-based marketing data queries."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_campaigns_in_period(
        self, company_id: uuid.UUID, start_date: datetime, end_date: datetime
    ) -> list[CampaignMetrics]:
        """Fetch all campaigns with aggregated metrics for the period."""
        stmt = select(CampaignModel).where(
            CampaignModel.company_id == company_id,
            CampaignModel.start_date >= start_date,
            CampaignModel.start_date <= end_date,
        )
        result = await self._session.execute(stmt)
        campaigns = result.scalars().all()

        metrics_list = []
        for campaign in campaigns:
            metrics = CampaignMetrics(
                campaign_id=campaign.campaign_id,
                campaign_name=campaign.name,
                platform=campaign.platform,
                period="monthly",  # Adjust based on actual period
                period_start=start_date,
                period_end=end_date,
                total_spend=campaign.total_spend,
                currency="USD",
                leads=campaign.leads,
                purchases=campaign.purchases,
                impressions=campaign.impressions,
                clicks=campaign.clicks,
                cpl=Decimal(0),
                cpp=None,
                cpc=Decimal(0),
                ctr=Decimal(0),
                roas=None,
            )
            metrics_list.append(metrics)

        return metrics_list

    async def get_campaign_metrics(
        self, company_id: uuid.UUID, campaign_id: str, start_date: datetime, end_date: datetime
    ) -> CampaignMetrics | None:
        """Fetch a single campaign's metrics."""
        stmt = select(CampaignModel).where(
            CampaignModel.company_id == company_id,
            CampaignModel.campaign_id == campaign_id,
            CampaignModel.start_date >= start_date,
            CampaignModel.start_date <= end_date,
        )
        result = await self._session.execute(stmt)
        campaign = result.scalar_one_or_none()

        if not campaign:
            return None

        return CampaignMetrics(
            campaign_id=campaign.campaign_id,
            campaign_name=campaign.name,
            platform=campaign.platform,
            period="monthly",
            period_start=start_date,
            period_end=end_date,
            total_spend=campaign.total_spend,
            currency="USD",
            leads=campaign.leads,
            purchases=campaign.purchases,
            impressions=campaign.impressions,
            clicks=campaign.clicks,
            cpl=Decimal(0),
            cpp=None,
            cpc=Decimal(0),
            ctr=Decimal(0),
            roas=None,
        )

    async def get_previous_period_metrics(
        self, company_id: uuid.UUID, campaign_id: str, start_date: datetime, end_date: datetime
    ) -> CampaignMetrics | None:
        """Fetch metrics for the same period last year."""
        period_length = end_date - start_date
        prev_start = start_date - timedelta(days=365)
        prev_end = end_date - timedelta(days=365)

        stmt = select(CampaignModel).where(
            CampaignModel.company_id == company_id,
            CampaignModel.campaign_id == campaign_id,
            CampaignModel.start_date >= prev_start,
            CampaignModel.start_date <= prev_end,
        )
        result = await self._session.execute(stmt)
        campaign = result.scalar_one_or_none()

        if not campaign:
            return None

        return CampaignMetrics(
            campaign_id=campaign.campaign_id,
            campaign_name=campaign.name,
            platform=campaign.platform,
            period="monthly",
            period_start=prev_start,
            period_end=prev_end,
            total_spend=campaign.total_spend,
            currency="USD",
            leads=campaign.leads,
            purchases=campaign.purchases,
            impressions=campaign.impressions,
            clicks=campaign.clicks,
            cpl=Decimal(0),
            cpp=None,
            cpc=Decimal(0),
            ctr=Decimal(0),
            roas=None,
        )

    async def get_total_marketing_spend(
        self, company_id: uuid.UUID, start_date: datetime, end_date: datetime
    ) -> Decimal:
        """Total spend across all campaigns."""
        stmt = select(func.coalesce(func.sum(CampaignModel.total_spend), Decimal(0))).where(
            CampaignModel.company_id == company_id,
            CampaignModel.start_date >= start_date,
            CampaignModel.start_date <= end_date,
        )
        result = await self._session.execute(stmt)
        return result.scalar()

    async def get_total_conversions(
        self, company_id: uuid.UUID, start_date: datetime, end_date: datetime
    ) -> tuple[int, int]:
        """Total leads and purchases."""
        stmt = select(
            func.coalesce(func.sum(CampaignModel.leads), 0),
            func.coalesce(func.sum(CampaignModel.purchases), 0),
        ).where(
            CampaignModel.company_id == company_id,
            CampaignModel.start_date >= start_date,
            CampaignModel.start_date <= end_date,
        )
        result = await self._session.execute(stmt)
        leads, purchases = result.one()
        return int(leads), int(purchases)
