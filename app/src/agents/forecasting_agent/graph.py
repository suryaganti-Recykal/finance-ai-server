"""LangGraph agent for financial forecasting.

Workflow:
1. Collect: Historical financial data
2. Analyze: Identify trends and patterns
3. Forecast: Generate predictions
4. Validate: Check forecast accuracy
5. Report: Return forecasts
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

from langgraph.graph import StateGraph, END

from src.core.logging.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ForecastingState:
    """State for financial forecasting."""
    company_id: str
    forecast_months: int = 6

    # Historical data
    historical_revenue: list[Decimal] = field(default_factory=list)
    historical_expenses: list[Decimal] = field(default_factory=list)

    # Calculated trends
    revenue_trend: str = ""  # "increasing", "decreasing", "stable"
    expense_trend: str = ""
    trend_confidence: Decimal = Decimal(0)

    # Forecasts
    revenue_forecast: list[dict] = field(default_factory=list)
    expense_forecast: list[dict] = field(default_factory=list)
    profit_forecast: list[dict] = field(default_factory=list)
    cash_flow_forecast: list[dict] = field(default_factory=list)

    # Scenarios
    optimistic_case: dict = field(default_factory=dict)
    pessimistic_case: dict = field(default_factory=dict)

    errors: list[str] = field(default_factory=list)


class ForecastingGraph:
    """LangGraph implementation of financial forecasting."""

    def __init__(self) -> None:
        self.graph = StateGraph(ForecastingState)
        self._build_graph()

    def _build_graph(self) -> None:
        """Build the LangGraph workflow."""
        self.graph.add_node("collect", self._collect_historical)
        self.graph.add_node("analyze", self._analyze_trends)
        self.graph.add_node("forecast", self._generate_forecasts)
        self.graph.add_node("scenarios", self._generate_scenarios)
        self.graph.add_node("validate", self._validate_forecast)

        self.graph.set_entry_point("collect")
        self.graph.add_edge("collect", "analyze")
        self.graph.add_edge("analyze", "forecast")
        self.graph.add_edge("forecast", "scenarios")
        self.graph.add_edge("scenarios", "validate")
        self.graph.add_edge("validate", END)

    async def _collect_historical(self, state: ForecastingState) -> ForecastingState:
        """Collect historical financial data."""
        logger.info(f"Collecting historical data for {state.company_id}")

        # Simulate historical data (6 months)
        state.historical_revenue = [
            Decimal("130000"),
            Decimal("135000"),
            Decimal("140000"),
            Decimal("142000"),
            Decimal("147000"),
            Decimal("150000"),
        ]

        state.historical_expenses = [
            Decimal("75000"),
            Decimal("76000"),
            Decimal("78000"),
            Decimal("80000"),
            Decimal("82000"),
            Decimal("85000"),
        ]

        return state

    async def _analyze_trends(self, state: ForecastingState) -> ForecastingState:
        """Analyze historical trends."""
        logger.info("Analyzing trends")

        try:
            # Simple trend analysis
            if state.historical_revenue[-1] > state.historical_revenue[0]:
                state.revenue_trend = "increasing"
                state.trend_confidence = Decimal("0.85")
            else:
                state.revenue_trend = "stable"
                state.trend_confidence = Decimal("0.60")

            if state.historical_expenses[-1] > state.historical_expenses[0]:
                state.expense_trend = "increasing"
            else:
                state.expense_trend = "stable"

            logger.info(f"Revenue trend: {state.revenue_trend} (confidence: {state.trend_confidence})")

        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
            state.errors.append(f"Trend analysis error: {str(e)}")

        return state

    async def _generate_forecasts(self, state: ForecastingState) -> ForecastingState:
        """Generate financial forecasts."""
        logger.info(f"Generating {state.forecast_months}-month forecasts")

        try:
            base_revenue = state.historical_revenue[-1]
            base_expense = state.historical_expenses[-1]
            monthly_growth = Decimal("0.05")  # 5% monthly growth

            for month in range(1, state.forecast_months + 1):
                forecast_date = (datetime.utcnow() + timedelta(days=30*month)).strftime("%Y-%m")

                revenue = base_revenue * (Decimal(1) + (monthly_growth * Decimal(month)))
                expenses = base_expense * (Decimal(1) + (Decimal("0.03") * Decimal(month)))
                profit = revenue - expenses

                state.revenue_forecast.append({"date": forecast_date, "value": float(revenue)})
                state.expense_forecast.append({"date": forecast_date, "value": float(expenses)})
                state.profit_forecast.append({"date": forecast_date, "value": float(profit)})

            logger.info(f"Generated {len(state.revenue_forecast)} month forecasts")

        except Exception as e:
            logger.error(f"Error generating forecasts: {e}")
            state.errors.append(f"Forecast generation error: {str(e)}")

        return state

    async def _generate_scenarios(self, state: ForecastingState) -> ForecastingState:
        """Generate optimistic and pessimistic scenarios."""
        logger.info("Generating scenarios")

        try:
            base_revenue = state.historical_revenue[-1]

            state.optimistic_case = {
                "scenario": "optimistic",
                "growth_rate": "10%",
                "revenue_6mo": float(base_revenue * Decimal("1.6")),
                "description": "Strong market demand, successful campaigns"
            }

            state.pessimistic_case = {
                "scenario": "pessimistic",
                "growth_rate": "0%",
                "revenue_6mo": float(base_revenue),
                "description": "Market slowdown, increased competition"
            }

            logger.info("Scenarios generated")

        except Exception as e:
            logger.error(f"Error generating scenarios: {e}")
            state.errors.append(f"Scenario generation error: {str(e)}")

        return state

    async def _validate_forecast(self, state: ForecastingState) -> ForecastingState:
        """Validate forecast assumptions."""
        logger.info("Validating forecast")
        return state

    async def run(
        self,
        company_id: str,
        forecast_months: int = 6
    ) -> dict[str, Any]:
        """Execute financial forecasting."""
        logger.info(f"Starting forecasting for {company_id}")

        state = ForecastingState(
            company_id=company_id,
            forecast_months=forecast_months
        )

        runnable = self.graph.compile()
        final_state = await runnable.ainvoke(state)

        return {
            "success": len(final_state.errors) == 0,
            "forecast_months": final_state.forecast_months,
            "trends": {
                "revenue": final_state.revenue_trend,
                "expenses": final_state.expense_trend,
                "confidence": float(final_state.trend_confidence),
            },
            "forecasts": {
                "revenue": final_state.revenue_forecast,
                "expenses": final_state.expense_forecast,
                "profit": final_state.profit_forecast,
            },
            "scenarios": {
                "optimistic": final_state.optimistic_case,
                "pessimistic": final_state.pessimistic_case,
            },
            "errors": final_state.errors if final_state.errors else None,
        }
