from datetime import datetime, timedelta, timezone

from fastapi import APIRouter

from src.api.deps import CurrentCompanyId, DbSession
from src.agents.expense_collection_agent import ExpenseCollectionGraph
from src.schemas.common import SuccessResponse

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.post("/sync", response_model=SuccessResponse[dict])
async def sync_expenses(
    company_id: CurrentCompanyId,
    db: DbSession,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> SuccessResponse[dict]:
    """Sync expenses from all configured sources (Zoho, Meta, Google Ads, Razorpay, Bank, CC).

    Called by n8n scheduler daily, or manually by admins.
    Uses LangGraph agent for orchestration.
    """
    # Set defaults
    now = datetime.now(timezone.utc)
    end = end_date or now
    start = start_date or (now - timedelta(days=7))

    # Execute LangGraph agent
    agent = ExpenseCollectionGraph(db)
    result = await agent.run(
        company_id=str(company_id),
        start_date=start,
        end_date=end
    )

    return SuccessResponse(
        data={
            "success": result["success"],
            "total_synced": result["total_synced"],
            "duplicates_removed": result["duplicates_removed"],
            "errors": result["errors"],
            "by_source": result.get("connector_results", {}),
            "error_details": result.get("error_details"),
        }
    )
