import uuid
from dataclasses import dataclass

from src.application.budgets.services.budget_service import BudgetMonitoringService
from src.application.shared.use_case import UseCase
from src.domain.budgets.entities.budget import BudgetSummary
from src.domain.budgets.repositories.budget import BudgetRepository


@dataclass(kw_only=True)
class CheckBudgetsInput:
    company_id: uuid.UUID
    fiscal_year: int
    quarter: int | None = None


class CheckBudgetsUseCase(UseCase[CheckBudgetsInput, BudgetSummary]):
    """Check all budgets and generate alerts for threshold crossings."""

    def __init__(self, budget_repo: BudgetRepository) -> None:
        self.budget_repo = budget_repo

    async def execute(self, input_data: CheckBudgetsInput) -> BudgetSummary:
        service = BudgetMonitoringService(self.budget_repo)
        summary = await service.check_all_budgets(
            input_data.company_id, input_data.fiscal_year, input_data.quarter
        )
        return summary
