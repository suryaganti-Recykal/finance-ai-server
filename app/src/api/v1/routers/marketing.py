from fastapi import APIRouter

from src.api.deps import CurrentCompanyId, DbSession
from src.agents.marketing_spend_agent import MarketingSpendGraph
from src.schemas.common import SuccessResponse

router = APIRouter(prefix="/marketing", tags=["Marketing"])


@router.get("", response_model=SuccessResponse[dict])
async def get_marketing_report(
    company_id: CurrentCompanyId,
    db: DbSession,
    time_period_days: int = 30,
) -> SuccessResponse[dict]:
    """Get comprehensive marketing report with KPIs and anomalies for all campaigns.

    Uses LangGraph agent for analysis and anomaly detection.
    """
    agent = MarketingSpendGraph(db)
    result = await agent.run(
        company_id=str(company_id),
        time_period_days=time_period_days
    )

    return SuccessResponse(data=result)
