from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from src.agents.finance_copilot_agent import FinanceCopilotGraph
from src.api.deps import CurrentCompanyId, DbSession
from src.schemas.common import SuccessResponse


class AskQuestionInput(BaseModel):
    """Input for asking a question to the Finance Copilot."""
    question: str
    conversation_history: list[dict] | None = None


router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/ask", response_model=SuccessResponse[dict[str, Any]])
async def ask_finance_question(
    company_id: CurrentCompanyId,
    db: DbSession,
    input_data: AskQuestionInput,
) -> SuccessResponse[dict[str, Any]]:
    """Ask a natural language question about your finances.

    Powered by Claude AI. Analyzes your financial data and provides
    intelligent answers with sources and confidence scores.

    Examples:
    - "What's our profit margin this month?"
    - "Is our revenue growing?"
    - "Which department is spending the most?"
    - "What's our cash runway?"
    """
    # Execute LangGraph agent
    agent = FinanceCopilotGraph(db)
    result = await agent.run(
        company_id=str(company_id),
        question=input_data.question,
        conversation_history=input_data.conversation_history
    )

    return SuccessResponse(
        data={
            "success": result["success"],
            "question": result["question"],
            "question_type": result["question_type"],
            "answer": result["answer"],
            "confidence": result["confidence"],
            "sources": result["sources"],
            "data_used": result["data_used"],
            "last_exchange": result["last_exchange"],
            "errors": result.get("errors"),
        }
    )
