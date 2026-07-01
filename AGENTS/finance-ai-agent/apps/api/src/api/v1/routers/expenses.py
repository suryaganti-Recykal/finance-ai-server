from datetime import datetime

from fastapi import APIRouter

from src.api.deps import CurrentCompanyId, DbSession
from src.application.expenses.use_cases.sync_expenses import (
    SyncExpensesInput,
    SyncExpensesOutput,
    SyncExpensesUseCase,
)
from src.schemas.common import SuccessResponse

router = APIRouter(prefix="/expenses", tags=["Expenses"])


class SyncExpensesResponseSchema(SuccessResponse[SyncExpensesOutput]):
    """Response schema for expense sync."""

    pass


@router.post("/sync", response_model=SuccessResponse[dict])
async def sync_expenses(
    company_id: CurrentCompanyId,
    db: DbSession,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> SuccessResponse[dict]:
    """Sync expenses from all configured sources (Zoho, Meta, Google Ads, Razorpay, Bank, CC).

    Called by n8n scheduler daily, or manually by admins.
    """
    use_case = SyncExpensesUseCase(db)
    result = await use_case.execute(
        SyncExpensesInput(company_id=company_id, start_date=start_date, end_date=end_date)
    )

    return SuccessResponse(
        data={
            "total_synced": result.total_synced,
            "total_duplicates": result.total_duplicates,
            "errors": result.errors,
            "sync_started_at": result.sync_started_at.isoformat(),
            "sync_completed_at": result.sync_completed_at.isoformat(),
        }
    )
