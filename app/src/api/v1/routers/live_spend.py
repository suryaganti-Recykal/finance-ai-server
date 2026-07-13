"""Live marketing spend data pulled directly from Recykal's Google Sheet.

No OAuth needed — the sheet is publicly viewable, so we fetch its CSV export
on every request. This is real data, not demo/sample data.
"""

from fastapi import APIRouter, HTTPException

from src.application.marketing.services.live_spend_service import LiveSpendService
from src.core.config.settings import get_settings
from src.core.logging.logger import get_logger
from src.infrastructure.connectors.marketing_spend_sheet import MarketingSpendSheetConnector
from src.schemas.common import SuccessResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/live", tags=["live-spend"])


@router.get("/marketing-spend", response_model=SuccessResponse[dict])
async def get_live_marketing_spend() -> SuccessResponse[dict]:
    """Fetch and summarize live marketing spend from the connected Google Sheet."""
    settings = get_settings()
    connector = MarketingSpendSheetConnector(
        sheet_id=settings.MARKETING_SHEET_ID,
        gid=settings.MARKETING_SHEET_GID,
    )

    try:
        records = await connector.fetch_records()
    except Exception as e:
        logger.error(f"Failed to fetch live marketing spend sheet: {e}")
        raise HTTPException(status_code=502, detail=f"Could not read Google Sheet: {e}")

    summary = LiveSpendService().summarize(records)
    return SuccessResponse(data=summary, message="Live marketing spend loaded from Google Sheets")


@router.get("/marketing-spend/raw", response_model=SuccessResponse[list[dict]])
async def get_live_marketing_spend_raw() -> SuccessResponse[list[dict]]:
    """Fetch raw line-item records (no aggregation) for detailed views/export."""
    settings = get_settings()
    connector = MarketingSpendSheetConnector(
        sheet_id=settings.MARKETING_SHEET_ID,
        gid=settings.MARKETING_SHEET_GID,
    )

    try:
        records = await connector.fetch_records()
    except Exception as e:
        logger.error(f"Failed to fetch live marketing spend sheet: {e}")
        raise HTTPException(status_code=502, detail=f"Could not read Google Sheet: {e}")

    data = [
        {
            "team": r.team,
            "sub_team": r.sub_team,
            "segment": r.segment,
            "type": r.type,
            "month": r.month,
            "sustainability": r.business_units.get("Sustainability", 0.0),
            "marketplace": r.business_units.get("Marketplace", 0.0),
            "drs": r.business_units.get("DRS", 0.0),
            "brand": r.business_units.get("Brand", 0.0),
            "total": r.total,
        }
        for r in records
    ]
    return SuccessResponse(data=data, message=f"{len(data)} live records loaded")
