from datetime import datetime
from typing import Any

from fastapi import APIRouter

from src.agents.monthly_report_agent import MonthlyReportGraph
from src.api.deps import CurrentCompanyId, DbSession
from src.schemas.common import SuccessResponse

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/monthly", response_model=SuccessResponse[dict[str, Any]])
async def generate_monthly_report(
    company_id: CurrentCompanyId,
    db: DbSession,
    year: int | None = None,
    month: int | None = None,
    report_format: str = "pdf",
) -> SuccessResponse[dict[str, Any]]:
    """Generate monthly financial report with AI-powered insights.

    Uses Claude to analyze financial data and generate insights/recommendations.
    Returns report summary with revenue, expenses, profit, and AI insights.
    """
    # Default to current month if not specified
    now = datetime.utcnow()
    year = year or now.year
    month = month or now.month

    # Execute LangGraph agent
    agent = MonthlyReportGraph(db)
    result = await agent.run(
        company_id=str(company_id),
        year=year,
        month=month,
        report_format=report_format
    )

    return SuccessResponse(
        data={
            "success": result["success"],
            "report_title": result["report_title"],
            "summary": result["summary"],
            "insights": result["insights"],
            "recommendations": result["recommendations"],
            "departments": result["departments"],
            "report_format": result["report_format"],
            "generated_at": result["generated_at"],
            "errors": result.get("errors"),
        }
    )
