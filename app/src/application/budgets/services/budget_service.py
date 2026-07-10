import uuid
from decimal import Decimal

from src.domain.budgets.entities.budget import BudgetStatus, BudgetSummary
from src.domain.budgets.repositories.budget import BudgetRepository


class BudgetMonitoringService:
    """Monitor budget utilization and trigger alerts at thresholds."""

    def __init__(self, budget_repo: BudgetRepository) -> None:
        self.repo = budget_repo

    async def check_all_budgets(
        self, company_id: uuid.UUID, fiscal_year: int, quarter: int | None = None
    ) -> BudgetSummary:
        """Check all budgets, calculate utilization, and generate alerts."""
        budgets = await self.repo.get_all_budgets(company_id, fiscal_year, quarter)

        total_budgeted = sum(b.budgeted_amount for b in budgets)
        total_spent = sum(b.spent_amount for b in budgets)
        overall_utilization = (
            (total_spent / total_budgeted * 100) if total_budgeted > 0 else Decimal(0)
        )

        # Check thresholds and generate alerts
        alerts = []
        for budget in budgets:
            for threshold in [80, 90, 100]:
                if budget.utilization_percent >= threshold:
                    # Check if we should trigger an alert
                    should_trigger = await self._should_trigger_alert(
                        company_id, budget.budget_id, threshold, budget.utilization_percent
                    )
                    if should_trigger:
                        alert = await self.repo.create_alert(
                            company_id,
                            budget.budget_id,
                            threshold,
                            budget.utilization_percent,
                        )
                        alerts.append(alert)

        return BudgetSummary(
            fiscal_year=fiscal_year,
            quarter=quarter,
            total_budgeted=total_budgeted,
            total_spent=total_spent,
            overall_utilization_percent=overall_utilization,
            budgets=budgets,
            active_alerts=alerts,
        )

    async def _should_trigger_alert(
        self,
        company_id: uuid.UUID,
        budget_id: uuid.UUID,
        threshold: int,
        utilization: Decimal,
    ) -> bool:
        """Check if we should trigger an alert (avoid duplicate alerts)."""
        # Check if threshold was already crossed before
        # If utilization is now >= threshold, trigger only if it wasn't before
        # For now, always trigger if above threshold
        # TODO: Check alert history to avoid duplicate notifications
        return utilization >= threshold

    async def get_budget_status(
        self, company_id: uuid.UUID, budget_id: uuid.UUID
    ) -> BudgetStatus | None:
        """Get current status of a single budget."""
        return await self.repo.get_budget_status(company_id, budget_id)

    async def acknowledge_alert(self, alert_id: uuid.UUID) -> None:
        """Mark an alert as acknowledged."""
        await self.repo.acknowledge_alert(alert_id)
