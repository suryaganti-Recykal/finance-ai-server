import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal

from src.domain.dashboard.entities.metrics import (
    BudgetUtilizationBreakdown,
    CampaignSpendBreakdown,
    DepartmentSpendBreakdown,
    KPIMetric,
    Trend,
)


class DashboardRepository(ABC):
    """Query expenses, revenues, collections, campaigns, budgets, etc. for dashboard aggregation."""

    @abstractmethod
    async def get_total_revenue(
        self, company_id: uuid.UUID, start_date: datetime, end_date: datetime
    ) -> Decimal:
        """Sum of all revenue in the period."""
        ...

    @abstractmethod
    async def get_total_expenses(
        self, company_id: uuid.UUID, start_date: datetime, end_date: datetime
    ) -> Decimal:
        """Sum of all expenses in the period."""
        ...

    @abstractmethod
    async def get_total_collections(
        self, company_id: uuid.UUID, start_date: datetime, end_date: datetime
    ) -> Decimal:
        """Sum of all collections/payments in the period."""
        ...

    @abstractmethod
    async def get_total_marketing_spend(
        self, company_id: uuid.UUID, start_date: datetime, end_date: datetime
    ) -> Decimal:
        """Sum of all marketing campaign spend."""
        ...

    @abstractmethod
    async def get_outstanding_receivables(self, company_id: uuid.UUID) -> Decimal:
        """Total value of unpaid invoices."""
        ...

    @abstractmethod
    async def get_outstanding_payables(self, company_id: uuid.UUID) -> Decimal:
        """Total value of unpaid bills/expenses (future concept)."""
        ...

    @abstractmethod
    async def get_cash_balance(self, company_id: uuid.UUID) -> Decimal | None:
        """Current cash on hand (from a cash account or manual input)."""
        ...

    @abstractmethod
    async def get_revenue_trend(
        self, company_id: uuid.UUID, start_date: datetime, end_date: datetime, period: str = "daily"
    ) -> Trend:
        """Revenue over time (daily/weekly/monthly)."""
        ...

    @abstractmethod
    async def get_expense_trend(
        self, company_id: uuid.UUID, start_date: datetime, end_date: datetime, period: str = "daily"
    ) -> Trend:
        """Expenses over time."""
        ...

    @abstractmethod
    async def get_collections_trend(
        self, company_id: uuid.UUID, start_date: datetime, end_date: datetime, period: str = "daily"
    ) -> Trend:
        """Collections (revenue received) over time."""
        ...

    @abstractmethod
    async def get_department_spend(
        self, company_id: uuid.UUID, start_date: datetime, end_date: datetime
    ) -> list[DepartmentSpendBreakdown]:
        """Spending by department (for pie chart)."""
        ...

    @abstractmethod
    async def get_budget_utilization(
        self, company_id: uuid.UUID
    ) -> list[BudgetUtilizationBreakdown]:
        """Budget vs. actual spend by department."""
        ...

    @abstractmethod
    async def get_campaign_spend(
        self, company_id: uuid.UUID, start_date: datetime, end_date: datetime
    ) -> list[CampaignSpendBreakdown]:
        """Marketing campaign spend breakdown."""
        ...
