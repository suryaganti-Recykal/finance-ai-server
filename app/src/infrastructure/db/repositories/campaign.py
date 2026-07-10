"""Campaign repository for database operations."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.models.campaign import CampaignModel


class CampaignRepositoryImpl:
    """Repository for campaign operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_campaigns_by_date_range(
        self,
        company_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> list[CampaignModel]:
        """Get campaigns within a date range."""
        query = select(CampaignModel).where(
            CampaignModel.company_id == company_id,
            CampaignModel.created_at >= start_date,
            CampaignModel.created_at <= end_date,
        )

        result = await self.db.execute(query)
        return result.scalars().all()
