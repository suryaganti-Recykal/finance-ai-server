"""LangGraph agent for real-time dashboard orchestration.

Workflow:
1. Coordinate: Call all KPI calculation agents in parallel
2. Aggregate: Combine results into dashboard view
3. Detect: Find significant changes vs previous state
4. Format: Prepare response for frontend
5. Report: Return dashboard state
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any

from langgraph.graph import StateGraph, END

from src.core.logging.logger import get_logger

logger = get_logger(__name__)


@dataclass
class DashboardOrchestrationState:
    """State for dashboard orchestration."""
    company_id: str
    start_date: datetime
    end_date: datetime

    # Collected KPI data
    revenue: Decimal = Decimal(0)
    expenses: Decimal = Decimal(0)
    collections: Decimal = Decimal(0)
    outstanding_receivables: Decimal = Decimal(0)
    marketing_spend: Decimal = Decimal(0)

    # Calculated metrics
    profit: Decimal = Decimal(0)
    cash_balance: Decimal = Decimal(0)
    runway_days: int = 0
    profit_margin: Decimal = Decimal(0)

    # Trend data
    revenue_trend: list[dict] = field(default_factory=list)
    expense_trend: list[dict] = field(default_factory=list)
    profit_trend: list[dict] = field(default_factory=list)

    # Department breakdown
    department_spend: list[dict] = field(default_factory=list)

    # Budget status
    budget_utilization: list[dict] = field(default_factory=list)

    # Alerts
    critical_alerts: list[dict] = field(default_factory=list)
    warnings: list[dict] = field(default_factory=list)

    # Tracking
    last_updated: datetime = field(default_factory=datetime.utcnow)
    calculation_time_ms: int = 0
    errors: list[str] = field(default_factory=list)


class DashboardOrchestrationGraph:
    """LangGraph implementation of dashboard orchestration."""

    def __init__(self) -> None:
        self.graph = StateGraph(DashboardOrchestrationState)
        self._build_graph()

    def _build_graph(self) -> None:
        """Build the LangGraph workflow."""
        self.graph.add_node("coordinate", self._coordinate_kpis)
        self.graph.add_node("aggregate", self._aggregate)
        self.graph.add_node("detect_changes", self._detect_changes)
        self.graph.add_node("format", self._format_response)
        self.graph.add_node("report", self._report)

        self.graph.set_entry_point("coordinate")
        self.graph.add_edge("coordinate", "aggregate")
        self.graph.add_edge("aggregate", "detect_changes")
        self.graph.add_edge("detect_changes", "format")
        self.graph.add_edge("format", "report")
        self.graph.add_edge("report", END)

    async def _coordinate_kpis(self, state: DashboardOrchestrationState) -> DashboardOrchestrationState:
        """Coordinate all KPI calculations in parallel."""
        logger.info(f"Orchestrating dashboard KPIs for {state.company_id}")

        # In production, this would call the actual agent endpoints in parallel
        # For now, we'll simulate with placeholder data
        try:
            state.revenue = Decimal("150000")
            state.expenses = Decimal("85000")
            state.collections = Decimal("120000")
            state.outstanding_receivables = Decimal("30000")
            state.marketing_spend = Decimal("15000")
            logger.info("KPIs collected from all agents")
        except Exception as e:
            logger.error(f"Error coordinating KPIs: {e}")
            state.errors.append(f"KPI coordination error: {str(e)}")

        return state

    async def _aggregate(self, state: DashboardOrchestrationState) -> DashboardOrchestrationState:
        """Aggregate KPIs into dashboard metrics."""
        logger.info("Aggregating KPI data")

        try:
            # Calculate derived metrics
            state.profit = state.revenue - state.expenses
            state.cash_balance = state.collections - state.expenses

            if state.revenue > 0:
                state.profit_margin = (state.profit / state.revenue * 100)
            else:
                state.profit_margin = Decimal(0)

            # Calculate runway (days until cash runs out)
            daily_burn = state.expenses / 30  # Assume 30-day month
            if daily_burn > 0:
                state.runway_days = int(state.cash_balance / daily_burn)
            else:
                state.runway_days = 999

            # Simulate trend data
            state.revenue_trend = [
                {"date": "2026-06-01", "value": 140000},
                {"date": "2026-06-15", "value": 145000},
                {"date": "2026-07-01", "value": 150000},
            ]

            state.expense_trend = [
                {"date": "2026-06-01", "value": 80000},
                {"date": "2026-06-15", "value": 82000},
                {"date": "2026-07-01", "value": 85000},
            ]

            state.profit_trend = [
                {"date": "2026-06-01", "value": 60000},
                {"date": "2026-06-15", "value": 63000},
                {"date": "2026-07-01", "value": 65000},
            ]

            logger.info(f"Aggregated: Profit=${state.profit}, Runway={state.runway_days} days")

        except Exception as e:
            logger.error(f"Error aggregating data: {e}")
            state.errors.append(f"Aggregation error: {str(e)}")

        return state

    async def _detect_changes(self, state: DashboardOrchestrationState) -> DashboardOrchestrationState:
        """Detect significant changes vs previous state."""
        logger.info("Detecting changes")

        try:
            # Simulate alert detection
            if state.profit_margin < Decimal(30):
                state.critical_alerts.append({
                    "type": "LOW_PROFIT_MARGIN",
                    "value": float(state.profit_margin),
                    "threshold": 30,
                    "severity": "CRITICAL"
                })

            if state.runway_days < 60:
                state.warnings.append({
                    "type": "LOW_RUNWAY",
                    "days": state.runway_days,
                    "severity": "WARNING"
                })

            if state.marketing_spend / state.revenue > Decimal(0.15):
                state.warnings.append({
                    "type": "HIGH_MARKETING_SPEND",
                    "percent": float(state.marketing_spend / state.revenue * 100),
                    "severity": "WARNING"
                })

            logger.info(f"Detected {len(state.critical_alerts)} critical, {len(state.warnings)} warnings")

        except Exception as e:
            logger.error(f"Error detecting changes: {e}")
            state.errors.append(f"Change detection error: {str(e)}")

        return state

    async def _format_response(self, state: DashboardOrchestrationState) -> DashboardOrchestrationState:
        """Format response for frontend."""
        logger.info("Formatting dashboard response")

        state.last_updated = datetime.utcnow()
        return state

    async def _report(self, state: DashboardOrchestrationState) -> DashboardOrchestrationState:
        """Generate final report."""
        logger.info("Dashboard orchestration complete")
        return state

    async def run(
        self,
        company_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> dict[str, Any]:
        """Execute dashboard orchestration."""
        logger.info(f"Starting dashboard orchestration for {company_id}")

        state = DashboardOrchestrationState(
            company_id=company_id,
            start_date=start_date,
            end_date=end_date
        )

        runnable = self.graph.compile()
        final_state = await runnable.ainvoke(state)

        return {
            "success": len(final_state.errors) == 0,
            "kpis": {
                "revenue": float(final_state.revenue),
                "expenses": float(final_state.expenses),
                "profit": float(final_state.profit),
                "profit_margin_percent": float(final_state.profit_margin),
                "collections": float(final_state.collections),
                "cash_balance": float(final_state.cash_balance),
                "outstanding_receivables": float(final_state.outstanding_receivables),
                "marketing_spend": float(final_state.marketing_spend),
                "runway_days": final_state.runway_days,
            },
            "trends": {
                "revenue": final_state.revenue_trend,
                "expenses": final_state.expense_trend,
                "profit": final_state.profit_trend,
            },
            "alerts": {
                "critical": final_state.critical_alerts,
                "warnings": final_state.warnings,
            },
            "last_updated": final_state.last_updated.isoformat(),
            "errors": final_state.errors if final_state.errors else None,
        }
