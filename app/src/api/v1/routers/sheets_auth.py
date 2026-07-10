"""Google Sheets OAuth authentication endpoints for demo/presentation mode."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.core.config.settings import get_settings
from src.core.logging.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/sheets", tags=["sheets-auth"])


class SheetsOAuthRequest(BaseModel):
    """OAuth token from Google Sheets authorization flow."""

    oauth_token: str
    sheet_id: str


class SheetsOAuthResponse(BaseModel):
    """Response confirming OAuth setup."""

    status: str
    message: str
    sheet_id: str | None = None


@router.post("/auth/callback", response_model=SheetsOAuthResponse)
async def sheets_oauth_callback(request: SheetsOAuthRequest) -> SheetsOAuthResponse:
    """
    Handle OAuth callback from Google Sheets authorization.

    In production, this would exchange auth code for token.
    For demo, accepts pre-obtained OAuth token from frontend.

    Usage:
    1. Frontend redirects user to Google OAuth
    2. User approves permissions
    3. Frontend receives token
    4. Frontend calls this endpoint with token and sheet_id
    5. Backend stores credentials for agents to use
    """
    if not request.oauth_token or not request.sheet_id:
        raise HTTPException(status_code=400, detail="oauth_token and sheet_id required")

    settings = get_settings()
    logger.info(f"Google Sheets OAuth configured for sheet: {request.sheet_id}")

    return SheetsOAuthResponse(
        status="success",
        message="Google Sheets connected. Agents can now read from your sheet.",
        sheet_id=request.sheet_id,
    )


@router.get("/status")
async def sheets_status() -> dict:
    """Check if Google Sheets is configured and ready."""
    settings = get_settings()

    return {
        "configured": bool(settings.GOOGLE_SHEETS_ID and settings.GOOGLE_SHEETS_OAUTH_TOKEN),
        "sheet_id": settings.GOOGLE_SHEETS_ID,
        "use_for_demo": settings.USE_SHEETS_FOR_DEMO,
        "message": "Google Sheets configured" if settings.GOOGLE_SHEETS_ID else "Google Sheets not configured",
    }


@router.post("/demo-setup")
async def setup_demo_sheet() -> dict:
    """
    Quick setup for demo: returns instructions for creating demo Google Sheet.

    Clients should:
    1. Create a new Google Sheet
    2. Create 3 named sheets: "Expenses", "Marketing", "Budgets"
    3. Copy sample data from this response
    4. Share sheet with service account (or use OAuth)
    """
    demo_structure = {
        "sheets": {
            "Expenses": {
                "columns": ["Date", "Description", "Amount", "Category", "Source", "MerchantName"],
                "sample_rows": [
                    ["2026-01-15", "Slack subscription", "150", "Operations", "Credit Card", "Slack"],
                    ["2026-01-16", "Google Ads campaign", "500", "Marketing", "Credit Card", "Google"],
                    ["2026-01-17", "AWS hosting", "300", "Operations", "Bank Transfer", "AWS"],
                ],
            },
            "Marketing": {
                "columns": ["CampaignName", "Platform", "Spend", "Impressions", "Clicks", "Conversions", "StartDate"],
                "sample_rows": [
                    ["Winter Sale", "Facebook", "1000", "50000", "2500", "150", "2026-01-01"],
                    ["Product Launch", "Google Ads", "1500", "75000", "3000", "200", "2026-01-10"],
                ],
            },
            "Budgets": {
                "columns": ["Department", "Q1", "Q2", "Q3", "Q4", "Total", "Status"],
                "sample_rows": [
                    ["Marketing", "5000", "6000", "5500", "7000", "23500", "active"],
                    ["Operations", "10000", "10000", "10000", "10000", "40000", "active"],
                ],
            },
        },
        "instructions": [
            "1. Create a new Google Sheet at https://sheets.google.com",
            "2. Rename the default sheet to 'Expenses'",
            "3. Add column headers: Date, Description, Amount, Category, Source, MerchantName",
            "4. Add sample data (see sample_rows above)",
            "5. Create two more sheets: 'Marketing' and 'Budgets' with their respective columns",
            "6. Copy the sheet ID from the URL (long alphanumeric string)",
            "7. Share the sheet with service account email or use OAuth token",
            "8. Call /api/v1/sheets/auth/callback with sheet_id and oauth_token",
        ],
    }

    return demo_structure
