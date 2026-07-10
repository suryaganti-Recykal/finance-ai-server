from typing import Any

from fastapi import APIRouter

from src.agents.email_distribution_agent import EmailDistributionGraph
from src.api.deps import CurrentCompanyId, DbSession
from src.schemas.common import SuccessResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("/send-report", response_model=SuccessResponse[dict[str, Any]])
async def send_report_email(
    company_id: CurrentCompanyId,
    db: DbSession,
    report_type: str = "daily",
) -> SuccessResponse[dict[str, Any]]:
    """Send financial report via email to stakeholders.

    Automatically fetches company users by role, personalizes content,
    and sends via SMTP. Requires SMTP_HOST, SMTP_USER, SMTP_PASSWORD env vars.
    """
    # Execute LangGraph agent
    agent = EmailDistributionGraph(db)
    result = await agent.run(
        company_id=str(company_id),
        report_type=report_type
    )

    return SuccessResponse(
        data={
            "success": result["success"],
            "emails_sent": result["emails_sent"],
            "total_recipients": result["total_recipients"],
            "delivery_status": result["delivery_status"],
            "errors": result.get("errors"),
        }
    )
