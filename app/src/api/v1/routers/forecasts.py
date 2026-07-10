from typing import Any

from fastapi import APIRouter

from src.agents.forecasting_agent import ForecastingGraph
from src.api.deps import CurrentCompanyId, DbSession
from src.schemas.common import SuccessResponse

router = APIRouter(prefix="/forecasts", tags=["Forecasting"])


@router.post("/financial", response_model=SuccessResponse[dict[str, Any]])
async def forecast_financial(
    company_id: CurrentCompanyId,
    db: DbSession,
    forecast_months: int = 6,
    historical_months: int = 12,
) -> SuccessResponse[dict[str, Any]]:
    """Generate financial forecasts for revenue, expenses, and profit.

    Analyzes up to N months of historical data and generates forecasts
    using exponential smoothing. Returns base case, optimistic, and pessimistic scenarios.
    """
    # Execute LangGraph agent
    agent = ForecastingGraph(db)
    result = await agent.run(
        company_id=str(company_id),
        forecast_months=forecast_months
    )

    return SuccessResponse(
        data={
            "success": result["success"],
            "forecast_months": result["forecast_months"],
            "trends": result["trends"],
            "forecasts": result["forecasts"],
            "scenarios": result["scenarios"],
            "errors": result.get("errors"),
        }
    )
