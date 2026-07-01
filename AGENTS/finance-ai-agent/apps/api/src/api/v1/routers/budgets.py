from fastapi import APIRouter

from src.api.deps import CurrentCompanyId, DbSession
from src.application.budgets.use_cases.check_budgets import CheckBudgetsInput, CheckBudgetsUseCase
from src.infrastructure.db.repositories.budget import BudgetRepositoryImpl
from src.schemas.budgets import BudgetSummarySchema
from src.schemas.common import SuccessResponse

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.get("", response_model=SuccessResponse[BudgetSummarySchema])
async def get_budget_summary(
    company_id: CurrentCompanyId,
    db: DbSession,
    fiscal_year: int,
    quarter: int | None = None,
) -> SuccessResponse[BudgetSummarySchema]:
    """Get budget status and alerts for all departments in a fiscal period."""
    repo = BudgetRepositoryImpl(db)
    use_case = CheckBudgetsUseCase(repo)

    summary = await use_case.execute(
        CheckBudgetsInput(company_id=company_id, fiscal_year=fiscal_year, quarter=quarter)
    )

    budgets = [
        {
            "budget_id": str(b.budget_id),
            "department_id": str(b.department_id),
            "department_name": b.department_name,
            "budgeted_amount": b.budgeted_amount,
            "spent_amount": b.spent_amount,
            "remaining_amount": b.remaining_amount,
            "utilization_percent": b.utilization_percent,
            "fiscal_year": b.fiscal_year,
            "quarter": b.quarter,
            "threshold_80_triggered": b.threshold_80_triggered,
            "threshold_90_triggered": b.threshold_90_triggered,
            "threshold_100_triggered": b.threshold_100_triggered,
        }
        for b in summary.budgets
    ]

    alerts = [
        {
            "alert_id": str(a.alert_id),
            "budget_id": str(a.budget_id),
            "department_name": a.department_name,
            "threshold_percent": a.threshold_percent,
            "utilization_percent": a.utilization_percent,
            "amount_spent": a.amount_spent,
            "amount_budgeted": a.amount_budgeted,
            "alert_level": a.alert_level,
            "triggered_at": a.triggered_at,
        }
        for a in summary.active_alerts
    ]

    return SuccessResponse(
        data=BudgetSummarySchema(
            fiscal_year=summary.fiscal_year,
            quarter=summary.quarter,
            total_budgeted=summary.total_budgeted,
            total_spent=summary.total_spent,
            overall_utilization_percent=summary.overall_utilization_percent,
            budgets=budgets,
            active_alerts=alerts,
        )
    )
