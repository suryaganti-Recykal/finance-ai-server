import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.budgets.entities.budget import BudgetAlert, BudgetStatus
from src.domain.budgets.repositories.budget import BudgetRepository
from src.infrastructure.db.models.budget import BudgetModel
from src.infrastructure.db.models.department import DepartmentModel
from src.infrastructure.db.models.expense import ExpenseModel


class BudgetRepositoryImpl(BudgetRepository):
    """SQLAlchemy-based budget queries."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_budget_status(
        self, company_id: uuid.UUID, budget_id: uuid.UUID
    ) -> BudgetStatus | None:
        """Fetch current status of a single budget."""
        stmt = select(BudgetModel, DepartmentModel.name).join(
            DepartmentModel, BudgetModel.department_id == DepartmentModel.id
        ).where(
            BudgetModel.company_id == company_id,
            BudgetModel.id == budget_id,
        )
        result = await self._session.execute(stmt)
        row = result.one_or_none()
        if not row:
            return None

        budget, dept_name = row
        utilization = (
            (budget.spent_amount / budget.budgeted_amount * 100)
            if budget.budgeted_amount > 0
            else Decimal(0)
        )

        return BudgetStatus(
            budget_id=budget.id,
            department_id=budget.department_id,
            department_name=dept_name,
            budgeted_amount=budget.budgeted_amount,
            spent_amount=budget.spent_amount,
            remaining_amount=budget.budgeted_amount - budget.spent_amount,
            utilization_percent=utilization,
            fiscal_year=budget.fiscal_year,
            quarter=budget.quarter,
            threshold_80_triggered=budget.threshold_80,
            threshold_90_triggered=budget.threshold_90,
            threshold_100_triggered=budget.threshold_100,
        )

    async def get_all_budgets(
        self, company_id: uuid.UUID, fiscal_year: int, quarter: int | None = None
    ) -> list[BudgetStatus]:
        """Fetch all budgets for a fiscal period."""
        stmt = select(BudgetModel, DepartmentModel.name).join(
            DepartmentModel, BudgetModel.department_id == DepartmentModel.id
        ).where(
            BudgetModel.company_id == company_id,
            BudgetModel.fiscal_year == fiscal_year,
        )
        if quarter:
            stmt = stmt.where(BudgetModel.quarter == quarter)

        result = await self._session.execute(stmt)
        rows = result.all()

        budgets = []
        for budget, dept_name in rows:
            utilization = (
                (budget.spent_amount / budget.budgeted_amount * 100)
                if budget.budgeted_amount > 0
                else Decimal(0)
            )
            budgets.append(
                BudgetStatus(
                    budget_id=budget.id,
                    department_id=budget.department_id,
                    department_name=dept_name,
                    budgeted_amount=budget.budgeted_amount,
                    spent_amount=budget.spent_amount,
                    remaining_amount=budget.budgeted_amount - budget.spent_amount,
                    utilization_percent=utilization,
                    fiscal_year=budget.fiscal_year,
                    quarter=budget.quarter,
                    threshold_80_triggered=budget.threshold_80,
                    threshold_90_triggered=budget.threshold_90,
                    threshold_100_triggered=budget.threshold_100,
                )
            )

        return budgets

    async def get_spend_to_date(
        self, company_id: uuid.UUID, department_id: uuid.UUID, fiscal_year: int
    ) -> Decimal:
        """Sum of expenses for a department."""
        stmt = select(func.coalesce(func.sum(ExpenseModel.amount), Decimal(0))).where(
            ExpenseModel.company_id == company_id,
            ExpenseModel.department_id == department_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar()

    async def check_threshold_crossing(
        self, company_id: uuid.UUID, budget_id: uuid.UUID, threshold: int
    ) -> bool:
        """Check if utilization crossed a specific threshold."""
        budget = await self.get_budget_status(company_id, budget_id)
        if not budget:
            return False
        return budget.utilization_percent >= threshold

    async def get_triggered_alerts(
        self, company_id: uuid.UUID
    ) -> list[BudgetAlert]:
        """Fetch all active (non-acknowledged) budget alerts."""
        # TODO: Implement alert storage and retrieval
        # For now, return empty list
        return []

    async def create_alert(
        self,
        company_id: uuid.UUID,
        budget_id: uuid.UUID,
        threshold_percent: int,
        utilization_percent: Decimal,
    ) -> BudgetAlert:
        """Create a budget threshold alert."""
        # TODO: Store alert in database
        # For now, return in-memory alert
        budget_status = await self.get_budget_status(company_id, budget_id)
        alert_level = "critical" if threshold_percent >= 100 else "warning"

        return BudgetAlert(
            alert_id=uuid.uuid4(),
            budget_id=budget_id,
            department_name=budget_status.department_name if budget_status else "",
            threshold_percent=threshold_percent,
            utilization_percent=utilization_percent,
            amount_spent=budget_status.spent_amount if budget_status else Decimal(0),
            amount_budgeted=budget_status.budgeted_amount if budget_status else Decimal(0),
            alert_level=alert_level,
            triggered_at=datetime.utcnow().isoformat(),
        )

    async def acknowledge_alert(self, alert_id: uuid.UUID) -> None:
        """Mark an alert as acknowledged."""
        # TODO: Update alert in database
        pass
