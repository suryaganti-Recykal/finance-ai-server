import uuid
from abc import ABC, abstractmethod
from decimal import Decimal

from src.domain.budgets.entities.budget import BudgetAlert, BudgetStatus


class BudgetRepository(ABC):
    """Query budget and spend data."""

    @abstractmethod
    async def get_budget_status(
        self, company_id: uuid.UUID, budget_id: uuid.UUID
    ) -> BudgetStatus | None:
        """Fetch current status of a single budget."""
        ...

    @abstractmethod
    async def get_all_budgets(
        self, company_id: uuid.UUID, fiscal_year: int, quarter: int | None = None
    ) -> list[BudgetStatus]:
        """Fetch all budgets for a fiscal period."""
        ...

    @abstractmethod
    async def get_spend_to_date(
        self, company_id: uuid.UUID, department_id: uuid.UUID, fiscal_year: int
    ) -> Decimal:
        """Sum of expenses for a department in the fiscal year."""
        ...

    @abstractmethod
    async def check_threshold_crossing(
        self, company_id: uuid.UUID, budget_id: uuid.UUID, threshold: int
    ) -> bool:
        """Check if utilization crossed a specific threshold (80, 90, 100)."""
        ...

    @abstractmethod
    async def get_triggered_alerts(
        self, company_id: uuid.UUID
    ) -> list[BudgetAlert]:
        """Fetch all active (non-acknowledged) budget alerts."""
        ...

    @abstractmethod
    async def create_alert(
        self,
        company_id: uuid.UUID,
        budget_id: uuid.UUID,
        threshold_percent: int,
        utilization_percent: Decimal,
    ) -> BudgetAlert:
        """Create a budget threshold alert."""
        ...

    @abstractmethod
    async def acknowledge_alert(self, alert_id: uuid.UUID) -> None:
        """Mark an alert as acknowledged (don't re-trigger)."""
        ...
