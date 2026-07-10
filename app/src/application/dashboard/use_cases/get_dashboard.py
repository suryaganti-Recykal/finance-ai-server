import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from src.application.shared.use_case import UseCase
from src.domain.dashboard.entities.metrics import KPIMetric
from src.domain.dashboard.repositories.dashboard import DashboardRepository


@dataclass(kw_only=True)
class GetDashboardInput:
    company_id: uuid.UUID
    start_date: datetime | None = None
    end_date: datetime | None = None


@dataclass(kw_only=True)
class GetDashboardOutput:
    period_start: datetime
    period_end: datetime
    kpis: dict[str, KPIMetric]


class GetDashboardUseCase(UseCase[GetDashboardInput, GetDashboardOutput]):
    """Calculate all dashboard KPIs for the given period."""

    def __init__(self, dashboard_repo: DashboardRepository) -> None:
        self.dashboard_repo = dashboard_repo

    async def execute(self, input_data: GetDashboardInput) -> GetDashboardOutput:
        now = datetime.now(UTC)
        period_end = input_data.end_date or now
        period_start = input_data.start_date or (now - timedelta(days=30))

        # Fetch all metrics in parallel (could use asyncio.gather for actual concurrency)
        total_revenue = await self.dashboard_repo.get_total_revenue(
            input_data.company_id, period_start, period_end
        )
        total_expenses = await self.dashboard_repo.get_total_expenses(
            input_data.company_id, period_start, period_end
        )
        total_collections = await self.dashboard_repo.get_total_collections(
            input_data.company_id, period_start, period_end
        )
        total_marketing_spend = await self.dashboard_repo.get_total_marketing_spend(
            input_data.company_id, period_start, period_end
        )
        outstanding_receivables = await self.dashboard_repo.get_outstanding_receivables(
            input_data.company_id
        )
        outstanding_payables = await self.dashboard_repo.get_outstanding_payables(
            input_data.company_id
        )
        cash_balance = await self.dashboard_repo.get_cash_balance(input_data.company_id)

        # Calculate derived metrics
        profit = total_revenue - total_expenses
        cash_available = (cash_balance or Decimal(0)) + total_collections
        net_cash = cash_available - outstanding_payables
        days_remaining = (period_end - period_start).days
        burn_rate = (total_expenses / days_remaining) if days_remaining > 0 else Decimal(0)
        runway_days = (net_cash / burn_rate) if burn_rate > 0 else Decimal(999)

        kpis = {
            "revenue": KPIMetric(
                label="Revenue",
                value=total_revenue,
                currency="USD",
            ),
            "expenses": KPIMetric(
                label="Expenses",
                value=total_expenses,
                currency="USD",
            ),
            "profit": KPIMetric(
                label="Profit",
                value=profit,
                currency="USD",
                change_direction="up" if profit >= Decimal(0) else "down",
            ),
            "collections": KPIMetric(
                label="Collections",
                value=total_collections,
                currency="USD",
            ),
            "cash_balance": KPIMetric(
                label="Cash Balance",
                value=cash_available,
                currency="USD",
            ),
            "outstanding_receivables": KPIMetric(
                label="Outstanding Receivables",
                value=outstanding_receivables,
                currency="USD",
            ),
            "marketing_spend": KPIMetric(
                label="Marketing Spend",
                value=total_marketing_spend,
                currency="USD",
            ),
            "runway": KPIMetric(
                label="Cash Runway",
                value=runway_days,
                currency="days",
            ),
        }

        return GetDashboardOutput(
            period_start=period_start,
            period_end=period_end,
            kpis=kpis,
        )
