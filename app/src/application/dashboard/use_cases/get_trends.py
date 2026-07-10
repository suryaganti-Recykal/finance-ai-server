import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from src.application.shared.use_case import UseCase
from src.domain.dashboard.entities.metrics import Trend
from src.domain.dashboard.repositories.dashboard import DashboardRepository


@dataclass(kw_only=True)
class GetTrendsInput:
    company_id: uuid.UUID
    start_date: datetime | None = None
    end_date: datetime | None = None


@dataclass(kw_only=True)
class GetTrendsOutput:
    revenue_trend: Trend
    expense_trend: Trend
    collections_trend: Trend


class GetTrendsUseCase(UseCase[GetTrendsInput, GetTrendsOutput]):
    """Fetch historical trends for revenue, expenses, and collections."""

    def __init__(self, dashboard_repo: DashboardRepository) -> None:
        self.dashboard_repo = dashboard_repo

    async def execute(self, input_data: GetTrendsInput) -> GetTrendsOutput:
        now = datetime.now(UTC)
        period_end = input_data.end_date or now
        period_start = input_data.start_date or (now - timedelta(days=90))

        revenue_trend = await self.dashboard_repo.get_revenue_trend(
            input_data.company_id, period_start, period_end
        )
        expense_trend = await self.dashboard_repo.get_expense_trend(
            input_data.company_id, period_start, period_end
        )
        collections_trend = await self.dashboard_repo.get_collections_trend(
            input_data.company_id, period_start, period_end
        )

        return GetTrendsOutput(
            revenue_trend=revenue_trend,
            expense_trend=expense_trend,
            collections_trend=collections_trend,
        )
