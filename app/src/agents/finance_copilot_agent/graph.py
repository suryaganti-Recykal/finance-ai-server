"""LangGraph agent for Finance Copilot - Natural Language Q&A.

Workflow:
1. Parse: Understand user question
2. Retrieve: Get relevant financial data
3. Reason: Apply financial logic
4. Generate: Create natural language response
5. Respond: Return answer to user
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from langgraph.graph import StateGraph, END

from src.core.logging.logger import get_logger

logger = get_logger(__name__)


@dataclass
class FinanceCopilotState:
    """State for finance copilot conversation."""
    company_id: str
    user_question: str
    conversation_history: list[dict] = field(default_factory=list)

    # Processing
    question_type: str = ""  # "kpi", "trend", "forecast", "comparison", "general"
    relevant_data: dict = field(default_factory=dict)
    analysis: str = ""

    # Response
    answer: str = ""
    confidence: float = 0.0
    sources: list[str] = field(default_factory=list)

    errors: list[str] = field(default_factory=list)


class FinanceCopilotGraph:
    """LangGraph implementation of Finance Copilot."""

    def __init__(self) -> None:
        self.graph = StateGraph(FinanceCopilotState)
        self._build_graph()

    def _build_graph(self) -> None:
        """Build the LangGraph workflow."""
        self.graph.add_node("parse", self._parse_question)
        self.graph.add_node("retrieve", self._retrieve_data)
        self.graph.add_node("reason", self._apply_reasoning)
        self.graph.add_node("generate", self._generate_response)
        self.graph.add_node("respond", self._format_response)

        self.graph.set_entry_point("parse")
        self.graph.add_edge("parse", "retrieve")
        self.graph.add_edge("retrieve", "reason")
        self.graph.add_edge("reason", "generate")
        self.graph.add_edge("generate", "respond")
        self.graph.add_edge("respond", END)

    async def _parse_question(self, state: FinanceCopilotState) -> FinanceCopilotState:
        """Parse user question to determine intent."""
        logger.info(f"Parsing question: {state.user_question}")

        try:
            question_lower = state.user_question.lower()

            if any(word in question_lower for word in ["revenue", "profit", "margin", "kpi"]):
                state.question_type = "kpi"
            elif any(word in question_lower for word in ["trend", "grow", "change", "increase"]):
                state.question_type = "trend"
            elif any(word in question_lower for word in ["forecast", "predict", "next", "future"]):
                state.question_type = "forecast"
            elif any(word in question_lower for word in ["compare", "vs", "versus", "difference"]):
                state.question_type = "comparison"
            else:
                state.question_type = "general"

            logger.info(f"Question type: {state.question_type}")

        except Exception as e:
            logger.error(f"Error parsing question: {e}")
            state.errors.append(f"Parse error: {str(e)}")

        return state

    async def _retrieve_data(self, state: FinanceCopilotState) -> FinanceCopilotState:
        """Retrieve relevant financial data."""
        logger.info(f"Retrieving data for {state.question_type} query")

        try:
            # Simulate data retrieval based on question type
            state.relevant_data = {
                "revenue": 150000,
                "expenses": 85000,
                "profit": 65000,
                "profit_margin": 0.433,
                "growth_vs_last_month": 0.08,
                "revenue_trend": "increasing",
                "confidence": 0.85,
            }

            state.sources = ["dashboard", "historical_data", "trends_analysis"]
            logger.info(f"Retrieved data from {len(state.sources)} sources")

        except Exception as e:
            logger.error(f"Error retrieving data: {e}")
            state.errors.append(f"Retrieval error: {str(e)}")

        return state

    async def _apply_reasoning(self, state: FinanceCopilotState) -> FinanceCopilotState:
        """Apply financial reasoning to answer question."""
        logger.info("Applying financial reasoning")

        try:
            # Simulate reasoning based on question type
            if state.question_type == "kpi":
                state.analysis = f"Based on current data, profit margin is {state.relevant_data['profit_margin']:.1%}"
            elif state.question_type == "trend":
                state.analysis = f"Revenue shows an {state.relevant_data['revenue_trend']} trend with {state.relevant_data['confidence']:.0%} confidence"
            elif state.question_type == "forecast":
                state.analysis = "Based on historical patterns and growth rate, projections show continued positive trajectory"
            elif state.question_type == "comparison":
                state.analysis = f"Revenue grew {state.relevant_data['growth_vs_last_month']:.1%} compared to last month"
            else:
                state.analysis = "Analysis complete based on available financial data"

            state.confidence = 0.85
            logger.info("Reasoning complete")

        except Exception as e:
            logger.error(f"Error in reasoning: {e}")
            state.errors.append(f"Reasoning error: {str(e)}")

        return state

    async def _generate_response(self, state: FinanceCopilotState) -> FinanceCopilotState:
        """Generate natural language response."""
        logger.info("Generating response")

        try:
            state.answer = f"{state.analysis}\n\nThis analysis is based on {len(state.sources)} data sources and has a confidence level of {state.confidence:.0%}."
            logger.info("Response generated")

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            state.errors.append(f"Generation error: {str(e)}")

        return state

    async def _format_response(self, state: FinanceCopilotState) -> FinanceCopilotState:
        """Format response for user."""
        logger.info("Formatting response")

        # Add to conversation history
        state.conversation_history.append({
            "role": "user",
            "content": state.user_question,
            "timestamp": datetime.utcnow().isoformat()
        })

        state.conversation_history.append({
            "role": "assistant",
            "content": state.answer,
            "timestamp": datetime.utcnow().isoformat()
        })

        return state

    async def run(
        self,
        company_id: str,
        question: str,
        conversation_history: list[dict] | None = None
    ) -> dict[str, Any]:
        """Execute finance copilot Q&A."""
        logger.info(f"Starting copilot for {company_id}: {question}")

        state = FinanceCopilotState(
            company_id=company_id,
            user_question=question,
            conversation_history=conversation_history or []
        )

        runnable = self.graph.compile()
        final_state = await runnable.ainvoke(state)

        return {
            "success": len(final_state.errors) == 0,
            "question": final_state.user_question,
            "answer": final_state.answer,
            "question_type": final_state.question_type,
            "confidence": final_state.confidence,
            "sources": final_state.sources,
            "conversation_history": final_state.conversation_history[-2:],  # Last exchange
            "errors": final_state.errors if final_state.errors else None,
        }
