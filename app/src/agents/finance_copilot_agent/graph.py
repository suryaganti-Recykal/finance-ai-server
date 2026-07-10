"""LangGraph agent for Finance Copilot - AI-powered Natural Language Q&A.

Workflow:
1. Parse: Use Claude to understand user question
2. Retrieve: Get relevant financial data from database
3. Reason: Use Claude for financial reasoning
4. Generate: Create natural language response with Claude
5. Respond: Format and return to user
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, cast

from anthropic import Anthropic
from langgraph.graph import END, StateGraph

from src.core.logging.logger import get_logger
from src.infrastructure.db.repositories.campaign import CampaignRepositoryImpl
from src.infrastructure.db.repositories.dashboard import DashboardRepositoryImpl
from src.infrastructure.db.session import AsyncSession

logger = get_logger(__name__)


@dataclass
class FinanceCopilotState:
    """State for finance copilot conversation."""
    company_id: str
    user_question: str
    conversation_history: list[dict] = field(default_factory=list)

    # Processing
    question_type: str = ""  # Determined by Claude
    relevant_data: dict = field(default_factory=dict)
    analysis: str = ""

    # Response
    answer: str = ""
    confidence: float = 0.9
    sources: list[str] = field(default_factory=list)

    errors: list[str] = field(default_factory=list)


class FinanceCopilotGraph:
    """LangGraph implementation of Finance Copilot."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.graph = StateGraph(FinanceCopilotState)
        self.dashboard_repo = DashboardRepositoryImpl(db)
        self.campaign_repo = CampaignRepositoryImpl(db)
        self.anthropic = Anthropic()
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
        """Parse user question using Claude to determine intent."""
        logger.info(f"Parsing question with Claude: {state.user_question}")

        try:
            # Use Claude to classify the question
            message = self.anthropic.messages.create(
                model="claude-opus-4-8",
                max_tokens=100,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Classify this financial question as one of: kpi, trend, forecast, comparison, or general.

Question: {state.user_question}

Respond with ONLY the classification word."""
                    }
                ]
            )

            state.question_type = message.content[0].text.strip().lower()
            if state.question_type not in ["kpi", "trend", "forecast", "comparison", "general"]:
                state.question_type = "general"

            logger.info(f"Question classified as: {state.question_type}")

        except Exception as e:
            logger.error(f"Error parsing question: {e}")
            state.errors.append(f"Parse error: {str(e)}")
            state.question_type = "general"

        return state

    async def _retrieve_data(self, state: FinanceCopilotState) -> FinanceCopilotState:
        """Retrieve relevant financial data from database."""
        logger.info(f"Retrieving financial data for {state.question_type} query")

        try:
            import uuid
            company_uuid = uuid.UUID(state.company_id) if isinstance(state.company_id, str) else state.company_id

            # Get last 30 and 60 days data
            end_date = datetime.utcnow()
            start_date_30 = end_date - timedelta(days=30)
            start_date_60 = end_date - timedelta(days=60)

            # Fetch all data in parallel
            (revenue_30, expenses_30, revenue_60, expenses_60, campaigns) = await asyncio.gather(
                self.dashboard_repo.get_total_revenue(company_uuid, start_date_30, end_date),
                self.dashboard_repo.get_total_expenses(company_uuid, start_date_30, end_date),
                self.dashboard_repo.get_total_revenue(company_uuid, start_date_60, start_date_30),
                self.dashboard_repo.get_total_expenses(company_uuid, start_date_60, start_date_30),
                self.campaign_repo.get_by_date_range(company_uuid, start_date_30, end_date),
            )

            revenue_30 = Decimal(str(revenue_30 or 0))
            expenses_30 = Decimal(str(expenses_30 or 0))
            revenue_60 = Decimal(str(revenue_60 or 0))
            expenses_60 = Decimal(str(expenses_60 or 0))

            # Calculate metrics
            state.relevant_data = {
                "revenue_30d": float(revenue_30),
                "expenses_30d": float(expenses_30),
                "profit_30d": float(revenue_30 - expenses_30),
                "profit_margin_30d": float((revenue_30 / revenue_30 * 100) if revenue_30 > 0 else 0),
                "growth_vs_60d": float(((revenue_30 - revenue_60) / revenue_60 * 100) if revenue_60 > 0 else 0),
                "expense_ratio": float((expenses_30 / revenue_30 * 100) if revenue_30 > 0 else 0),
            }

            # Add campaign data if available
            if campaigns:
                total_campaign_spend = sum(float(getattr(c, 'budget_spent', 0) or 0) for c in campaigns)
                total_campaign_revenue = sum(float(getattr(c, 'revenue_generated', 0) or 0) for c in campaigns)
                state.relevant_data["campaign_spend"] = total_campaign_spend
                state.relevant_data["campaign_roi"] = total_campaign_revenue / total_campaign_spend if total_campaign_spend > 0 else 0

            state.sources = ["revenue", "expenses", "campaigns", "historical_data"]
            logger.info(f"Retrieved data from {len(state.sources)} sources")

        except Exception as e:
            logger.error(f"Error retrieving data: {e}")
            state.errors.append(f"Retrieval error: {str(e)}")

        return state

    async def _apply_reasoning(self, state: FinanceCopilotState) -> FinanceCopilotState:
        """Apply financial reasoning using Claude."""
        logger.info("Applying financial reasoning")

        try:
            data_context = f"""
Financial Data:
- 30-day Revenue: ${state.relevant_data.get('revenue_30d', 0):,.2f}
- 30-day Expenses: ${state.relevant_data.get('expenses_30d', 0):,.2f}
- 30-day Profit: ${state.relevant_data.get('profit_30d', 0):,.2f}
- Profit Margin: {state.relevant_data.get('profit_margin_30d', 0):.1f}%
- Growth vs 60 days: {state.relevant_data.get('growth_vs_60d', 0):.1f}%
- Expense Ratio: {state.relevant_data.get('expense_ratio', 0):.1f}%
"""
            if "campaign" in state.relevant_data:
                data_context += f"- Campaign Spend: ${state.relevant_data.get('campaign_spend', 0):,.2f}\n"
                data_context += f"- Campaign ROI: {state.relevant_data.get('campaign_roi', 0):.2f}x\n"

            # Use Claude for reasoning
            message = self.anthropic.messages.create(
                model="claude-opus-4-8",
                max_tokens=300,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Based on this financial data, provide analysis for the question.
Question Type: {state.question_type}
Question: {state.user_question}

{data_context}

Provide a brief analysis (2-3 sentences) of what the data shows and what it means for the business."""
                    }
                ]
            )

            state.analysis = message.content[0].text
            logger.info("Reasoning complete")

        except Exception as e:
            logger.error(f"Error in reasoning: {e}")
            state.errors.append(f"Reasoning error: {str(e)}")
            state.analysis = "Unable to generate analysis at this time."

        return state

    async def _generate_response(self, state: FinanceCopilotState) -> FinanceCopilotState:
        """Generate natural language response using Claude."""
        logger.info("Generating AI response")

        try:
            # Use Claude to generate the final answer
            message = self.anthropic.messages.create(
                model="claude-opus-4-8",
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": f"""You are a financial AI assistant. Answer this question based on the analysis:

Question: {state.user_question}

Analysis: {state.analysis}

Available Data Sources: {', '.join(state.sources)}

Provide a comprehensive, business-focused answer that:
1. Answers the user's question directly
2. References the relevant data
3. Provides actionable insights
4. Is conversational but professional"""
                    }
                ]
            )

            state.answer = message.content[0].text
            state.confidence = 0.9
            logger.info("Response generated successfully")

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            state.errors.append(f"Generation error: {str(e)}")
            state.answer = "I encountered an error while generating a response. Please try again."

        return state

    async def _format_response(self, state: FinanceCopilotState) -> FinanceCopilotState:
        """Format response and add to conversation history."""
        logger.info("Formatting response")

        try:
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

            logger.info("Response formatted and added to history")

        except Exception as e:
            logger.error(f"Error formatting response: {e}")
            state.errors.append(f"Format error: {str(e)}")

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
        final_state = cast(dict[str, Any], await runnable.ainvoke(state))

        return {
            "success": len(final_state["errors"]) == 0,
            "question": final_state["user_question"],
            "question_type": final_state["question_type"],
            "answer": final_state["answer"],
            "confidence": final_state["confidence"],
            "sources": final_state["sources"] if final_state["sources"] else [],
            "data_used": final_state["relevant_data"] if final_state["relevant_data"] else {},
            "last_exchange": final_state["conversation_history"][-2:] if len(final_state["conversation_history"]) >= 2 else [],
            "errors": final_state["errors"] if final_state["errors"] else None,
        }
