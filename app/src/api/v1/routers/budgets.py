from fastapi import APIRouter

from src.api.deps import CurrentCompanyId, DbSession
from src.agents.budget_monitoring_agent import BudgetMonitoringGraph
from src.schemas.common import SuccessResponse

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.get("", response_model=SuccessResponse[dict])
async def get_budget_summary(
    company_id: CurrentCompanyId,
    db: DbSession,
    fiscal_year: int,
    quarter: int | None = None,
) -> SuccessResponse[dict]:
    """Get budget status and alerts for all departments in a fiscal period.

    Uses LangGraph agent for budget monitoring and threshold checking.
    """
    agent = BudgetMonitoringGraph(db)
    result = await agent.run(
        company_id=str(company_id),
        fiscal_year=fiscal_year,
        quarter=quarter
    )

    return SuccessResponse(data=result)
