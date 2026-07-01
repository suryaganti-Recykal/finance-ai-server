import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal

from src.domain.marketing.entities.metrics import CampaignMetrics


class MarketingRepository(ABC):
    """Query campaign spend and performance data."""

    @abstractmethod
    async def get_campaigns_in_period(
        self, company_id: uuid.UUID, start_date: datetime, end_date: datetime
    ) -> list[CampaignMetrics]:
        """Fetch all campaigns with metrics for the period."""
        ...

    @abstractmethod
    async def get_campaign_metrics(
        self, company_id: uuid.UUID, campaign_id: str, start_date: datetime, end_date: datetime
    ) -> CampaignMetrics | None:
        """Fetch metrics for a single campaign."""
        ...

    @abstractmethod
    async def get_previous_period_metrics(
        self, company_id: uuid.UUID, campaign_id: str, start_date: datetime, end_date: datetime
    ) -> CampaignMetrics | None:
        """Fetch metrics for the same period last year/month for comparison."""
        ...

    @abstractmethod
    async def get_total_marketing_spend(
        self, company_id: uuid.UUID, start_date: datetime, end_date: datetime
    ) -> Decimal:
        """Total spend across all campaigns."""
        ...

    @abstractmethod
    async def get_total_conversions(
        self, company_id: uuid.UUID, start_date: datetime, end_date: datetime
    ) -> tuple[int, int]:
        """Total leads and purchases across all campaigns."""
        ...
