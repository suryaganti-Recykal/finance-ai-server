"""LangGraph agent for financial forecasting using real historical data.

Workflow:
1. Collect: Fetch actual historical financial data from database
2. Analyze: Identify trends, seasonality, and growth patterns
3. Forecast: Generate predictions using exponential smoothing
4. Scenarios: Create optimistic and pessimistic cases
5. Validate: Check forecast reasonableness
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, cast

from langgraph.graph import END, StateGraph

from src.core.logging.logger import get_logger
from src.infrastructure.db.repositories.dashboard import DashboardRepositoryImpl
from src.infrastructure.db.session import AsyncSession

logger = get_logger(__name__)


@dataclass
class ForecastingState:
    """State for financial forecasting."""
    company_id: str
    forecast_months: int = 6
    historical_months: int = 12

    # Historical data
    historical_revenue: list[Decimal] = field(default_factory=list)
    historical_expenses: list[Decimal] = field(default_factory=list)
    historical_dates: list[str] = field(default_factory=list)

    # Calculated trends
    revenue_trend: str = ""  # "increasing", "decreasing", "stable"
    expense_trend: str = ""
    revenue_growth_rate: Decimal = Decimal(0)
    expense_growth_rate: Decimal = Decimal(0)
    trend_confidence: Decimal = Decimal(0)

    # Forecasts
    revenue_forecast: list[dict] = field(default_factory=list)
    expense_forecast: list[dict] = field(default_factory=list)
    profit_forecast: list[dict] = field(default_factory=list)

    # Scenarios
    optimistic_case: dict = field(default_factory=dict)
    pessimistic_case: dict = field(default_factory=dict)
    base_case: dict = field(default_factory=dict)

    errors: list[str] = field(default_factory=list)


class ForecastingGraph:
    """LangGraph implementation of financial forecasting."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.graph = StateGraph(ForecastingState)
        self.dashboard_repo = DashboardRepositoryImpl(db)
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
        """Collect actual historical financial data from database."""
        logger.info(f"Collecting {state.historical_months}-month historical data for {state.company_id}")

        try:
            import uuid
            company_uuid = uuid.UUID(state.company_id) if isinstance(state.company_id, str) else state.company_id

            # Fetch data for last N months
            for month in range(state.historical_months, 0, -1):
                month_start = datetime.utcnow() - timedelta(days=30 * month)
                month_end = datetime.utcnow() - timedelta(days=30 * (month - 1))
                month_str = month_start.strftime("%Y-%m")

                revenue = await self.dashboard_repo.get_total_revenue(
                    company_uuid, month_start, month_end
                )
                expenses = await self.dashboard_repo.get_total_expenses(
                    company_uuid, month_start, month_end
                )

                state.historical_dates.append(month_str)
                state.historical_revenue.append(Decimal(str(revenue or 0)))
                state.historical_expenses.append(Decimal(str(expenses or 0)))

            logger.info(f"Collected {len(state.historical_revenue)} months of historical data")

        except Exception as e:
            logger.error(f"Error collecting historical data: {e}")
            state.errors.append(f"Collection error: {str(e)}")

        return state

    async def _analyze_trends(self, state: ForecastingState) -> ForecastingState:
        """Analyze historical trends using real data."""
        logger.info("Analyzing trends from historical data")

        try:
            if not state.historical_revenue or len(state.historical_revenue) < 2:
                logger.warning("Not enough historical data for trend analysis")
                return state

            # Calculate growth rates
            revenue_start = state.historical_revenue[0]
            revenue_end = state.historical_revenue[-1]
            expense_start = state.historical_expenses[0]
            expense_end = state.historical_expenses[-1]

            if revenue_start > 0:
                total_rev_growth = (revenue_end - revenue_start) / revenue_start
                state.revenue_growth_rate = Decimal(str(total_rev_growth / len(state.historical_revenue)))
            else:
                state.revenue_growth_rate = Decimal(0)

            if expense_start > 0:
                total_exp_growth = (expense_end - expense_start) / expense_start
                state.expense_growth_rate = Decimal(str(total_exp_growth / len(state.historical_expenses)))
            else:
                state.expense_growth_rate = Decimal(0)

            # Determine trend direction
            if state.revenue_growth_rate > Decimal("0.02"):
                state.revenue_trend = "increasing"
                state.trend_confidence = Decimal("0.85") if revenue_end > revenue_start else Decimal("0.60")
            elif state.revenue_growth_rate < Decimal("-0.02"):
                state.revenue_trend = "decreasing"
                state.trend_confidence = Decimal("0.85")
            else:
                state.revenue_trend = "stable"
                state.trend_confidence = Decimal("0.70")

            if state.expense_growth_rate > Decimal("0.02"):
                state.expense_trend = "increasing"
            elif state.expense_growth_rate < Decimal("-0.02"):
                state.expense_trend = "decreasing"
            else:
                state.expense_trend = "stable"

            logger.info(f"Revenue trend: {state.revenue_trend} ({float(state.revenue_growth_rate)*100:.2f}% monthly), "
                       f"Expense trend: {state.expense_trend} ({float(state.expense_growth_rate)*100:.2f}% monthly)")

        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
            state.errors.append(f"Analysis error: {str(e)}")

        return state

    async def _generate_forecasts(self, state: ForecastingState) -> ForecastingState:
        """Generate forecasts using exponential smoothing on real historical data."""
        logger.info(f"Generating {state.forecast_months}-month forecasts")

        try:
            if not state.historical_revenue:
                logger.warning("No historical data for forecasting")
                return state

            # Use last 3 months average as baseline
            base_revenue = sum(state.historical_revenue[-3:]) / 3 if len(state.historical_revenue) >= 3 else state.historical_revenue[-1]
            base_expense = sum(state.historical_expenses[-3:]) / 3 if len(state.historical_expenses) >= 3 else state.historical_expenses[-1]

            # Use calculated growth rate or default to moderate growth
            growth_rate = state.revenue_growth_rate if state.revenue_growth_rate != Decimal(0) else Decimal("0.03")
            expense_growth = state.expense_growth_rate if state.expense_growth_rate != Decimal(0) else Decimal("0.02")

            for month in range(1, state.forecast_months + 1):
                forecast_date = (datetime.utcnow() + timedelta(days=30 * month)).strftime("%Y-%m")

                # Exponential smoothing: each month builds on previous
                revenue = base_revenue * ((Decimal(1) + growth_rate) ** Decimal(month))
                expenses = base_expense * ((Decimal(1) + expense_growth) ** Decimal(month))
                profit = revenue - expenses

                state.revenue_forecast.append({"date": forecast_date, "value": float(revenue)})
                state.expense_forecast.append({"date": forecast_date, "value": float(expenses)})
                state.profit_forecast.append({"date": forecast_date, "value": float(profit)})

            logger.info(f"Generated {len(state.revenue_forecast)} month forecasts with growth rate {float(growth_rate)*100:.1f}%")

        except Exception as e:
            logger.error(f"Error generating forecasts: {e}")
            state.errors.append(f"Forecast generation error: {str(e)}")

        return state

    async def _generate_scenarios(self, state: ForecastingState) -> ForecastingState:
        """Generate optimistic and pessimistic scenarios based on real trends."""
        logger.info("Generating scenarios")

        try:
            if not state.revenue_forecast:
                logger.warning("No forecasts for scenario generation")
                return state

            base_revenue = state.revenue_forecast[-1]["value"]
            base_expense = state.expense_forecast[-1]["value"]

            # Base case: use calculated growth
            state.base_case = {
                "scenario": "base",
                "description": f"Trend-based forecast with {float(state.revenue_growth_rate)*100:.1f}% revenue growth",
                "revenue_6mo": float(base_revenue),
                "expense_6mo": float(base_expense),
                "profit_6mo": float(base_revenue - base_expense),
            }

            # Optimistic: +50% more growth than base
            optimistic_growth = state.revenue_growth_rate * Decimal("1.5")
            last_revenue = state.historical_revenue[-1]
            optimistic_revenue = last_revenue * ((Decimal(1) + optimistic_growth) ** Decimal(6))

            state.optimistic_case = {
                "scenario": "optimistic",
                "growth_rate": f"{float(optimistic_growth)*100:.1f}%",
                "revenue_6mo": float(optimistic_revenue),
                "description": "Strong market demand, successful campaigns, market expansion",
            }

            # Pessimistic: growth drops to zero
            state.pessimistic_case = {
                "scenario": "pessimistic",
                "growth_rate": "0%",
                "revenue_6mo": float(last_revenue),
                "description": "Market slowdown, increased competition, economic headwinds",
            }

            logger.info("Scenarios generated: base, optimistic, pessimistic")

        except Exception as e:
            logger.error(f"Error generating scenarios: {e}")
            state.errors.append(f"Scenario generation error: {str(e)}")

        return state

    async def _validate_forecast(self, state: ForecastingState) -> ForecastingState:
        """Validate forecast reasonableness."""
        logger.info("Validating forecast")

        try:
            # Check for reasonable forecasts
            if state.revenue_forecast:
                latest_forecast = state.revenue_forecast[-1]["value"]
                last_actual = float(state.historical_revenue[-1]) if state.historical_revenue else 0

                # Warn if forecast deviates too much from trends
                deviation = abs(latest_forecast - last_actual) / last_actual if last_actual > 0 else 0
                if deviation > 1.0:  # More than 100% change
                    logger.warning(f"Large forecast deviation detected: {float(deviation)*100:.1f}%")

            logger.info("Forecast validation complete")

        except Exception as e:
            logger.error(f"Error validating forecast: {e}")
            state.errors.append(f"Validation error: {str(e)}")

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
        final_state = cast(dict[str, Any], await runnable.ainvoke(state))

        return {
            "success": len(final_state["errors"]) == 0,
            "forecast_months": final_state["forecast_months"],
            "trends": {
                "revenue": final_state["revenue_trend"],
                "expenses": final_state["expense_trend"],
                "confidence": float(final_state["trend_confidence"]),
            },
            "forecasts": {
                "revenue": final_state["revenue_forecast"],
                "expenses": final_state["expense_forecast"],
                "profit": final_state["profit_forecast"],
            },
            "scenarios": {
                "optimistic": final_state["optimistic_case"],
                "pessimistic": final_state["pessimistic_case"],
            },
            "errors": final_state["errors"] if final_state["errors"] else None,
        }
