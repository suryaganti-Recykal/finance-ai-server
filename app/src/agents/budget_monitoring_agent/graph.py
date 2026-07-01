"""LangGraph agent for budget monitoring and alert generation.

Workflow:
1. Fetch: Get budgets and current spending for each department
2. Calculate: Compute utilization % and remaining budget
3. Check: Check thresholds (80%, 90%, 100%)
4. Alert: Generate alerts for exceeded thresholds
5. Report: Aggregate and return summary
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any

from langgraph.graph import StateGraph, END

from src.core.logging.logger import get_logger
from src.infrastructure.db.repositories.budget import BudgetRepositoryImpl
from src.infrastructure.db.repositories.expense import ExpenseRepositoryImpl
from src.infrastructure.db.session import AsyncSession

logger = get_logger(__name__)


@dataclass
class BudgetStatus:
    """Budget status for a department."""
    budget_id: str
    department_id: str
    department_name: str
    budgeted_amount: Decimal
    spent_amount: Decimal
    remaining_amount: Decimal
    utilization_percent: Decimal
    fiscal_year: int
    quarter: int | None
    threshold_80_triggered: bool
    threshold_90_triggered: bool
    threshold_100_triggered: bool


@dataclass
class BudgetAlert:
    """Alert for budget threshold."""
    alert_id: str
    budget_id: str
    department_name: str
    threshold_percent: int
    utilization_percent: Decimal
    amount_spent: Decimal
    amount_budgeted: Decimal
    alert_level: str  # "normal", "warning", "critical", "overbudget"
    triggered_at: datetime


@dataclass
class BudgetMonitoringState:
    """State for budget monitoring workflow."""
    company_id: str
    fiscal_year: int
    quarter: int | None = None

    # Intermediate results
    budgets: list[Any] = field(default_factory=list)
    budget_statuses: list[BudgetStatus] = field(default_factory=list)
    alerts: list[BudgetAlert] = field(default_factory=list)

    # Aggregates
    total_budgeted: Decimal = Decimal(0)
    total_spent: Decimal = Decimal(0)
    overall_utilization_percent: Decimal = Decimal(0)

    # Tracking
    errors: list[str] = field(default_factory=list)
    alert_count: int = 0


class BudgetMonitoringGraph:
    """LangGraph implementation of budget monitoring."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.graph = StateGraph(BudgetMonitoringState)
        self.budget_repo = BudgetRepositoryImpl(db)
        self.expense_repo = ExpenseRepositoryImpl(db)
        self._build_graph()

    def _build_graph(self) -> None:
        """Build the LangGraph workflow."""
        self.graph.add_node("fetch", self._fetch_budgets)
        self.graph.add_node("calculate", self._calculate_utilization)
        self.graph.add_node("check_thresholds", self._check_thresholds)
        self.graph.add_node("generate_alerts", self._generate_alerts)
        self.graph.add_node("aggregate", self._aggregate)
        self.graph.add_node("report", self._report)

        self.graph.set_entry_point("fetch")
        self.graph.add_edge("fetch", "calculate")
        self.graph.add_edge("calculate", "check_thresholds")
        self.graph.add_edge("check_thresholds", "generate_alerts")
        self.graph.add_edge("generate_alerts", "aggregate")
        self.graph.add_edge("aggregate", "report")
        self.graph.add_edge("report", END)

    async def _fetch_budgets(self, state: BudgetMonitoringState) -> BudgetMonitoringState:
        """Fetch budgets for fiscal period."""
        logger.info(f"Fetching budgets for {state.company_id}, FY {state.fiscal_year}")

        try:
            budgets = await self.budget_repo.get_by_fiscal_year(
                state.company_id,
                state.fiscal_year,
                state.quarter
            )

            state.budgets = budgets
            logger.info(f"Fetched {len(budgets)} budgets")

        except Exception as e:
            logger.error(f"Error fetching budgets: {e}")
            state.errors.append(f"Fetch error: {str(e)}")

        return state

    async def _calculate_utilization(self, state: BudgetMonitoringState) -> BudgetMonitoringState:
        """Calculate spending and utilization for each department."""
        logger.info("Calculating utilization")

        for budget in state.budgets:
            try:
                # Get total spent for department
                spent = await self.expense_repo.sum_by_department(
                    state.company_id,
                    budget.department_id,
                    state.fiscal_year,
                    state.quarter
                )

                # Calculate metrics
                utilization = (spent / budget.budgeted_amount * 100) if budget.budgeted_amount > 0 else Decimal(0)
                remaining = budget.budgeted_amount - spent

                status = BudgetStatus(
                    budget_id=str(budget.id),
                    department_id=str(budget.department_id),
                    department_name=budget.department.name,
                    budgeted_amount=budget.budgeted_amount,
                    spent_amount=spent,
                    remaining_amount=remaining,
                    utilization_percent=utilization,
                    fiscal_year=state.fiscal_year,
                    quarter=state.quarter,
                    threshold_80_triggered=False,
                    threshold_90_triggered=False,
                    threshold_100_triggered=False,
                )

                state.budget_statuses.append(status)

                logger.info(f"{budget.department.name}: {utilization}% utilized")

            except Exception as e:
                logger.error(f"Error calculating utilization for {budget.department.name}: {e}")
                state.errors.append(f"Calculation error: {str(e)}")

        return state

    async def _check_thresholds(self, state: BudgetMonitoringState) -> BudgetMonitoringState:
        """Check threshold triggers for each budget."""
        logger.info("Checking thresholds")

        for status in state.budget_statuses:
            # Check thresholds
            if status.utilization_percent >= 100:
                status.threshold_100_triggered = True
                status.threshold_90_triggered = True
                status.threshold_80_triggered = True
            elif status.utilization_percent >= 90:
                status.threshold_90_triggered = True
                status.threshold_80_triggered = True
            elif status.utilization_percent >= 80:
                status.threshold_80_triggered = True

        triggered = sum(1 for s in state.budget_statuses if s.threshold_80_triggered)
        logger.info(f"Thresholds triggered for {triggered} departments")
        return state

    async def _generate_alerts(self, state: BudgetMonitoringState) -> BudgetMonitoringState:
        """Generate alerts for triggered thresholds."""
        logger.info("Generating alerts")

        for status in state.budget_statuses:
            # Determine alert level
            if status.threshold_100_triggered:
                alert_level = "OVERBUDGET"
                threshold_percent = 100
            elif status.threshold_90_triggered:
                alert_level = "CRITICAL"
                threshold_percent = 90
            elif status.threshold_80_triggered:
                alert_level = "WARNING"
                threshold_percent = 80
            else:
                alert_level = "NORMAL"
                threshold_percent = 0

            # Create alert if any threshold triggered
            if status.threshold_80_triggered or status.threshold_90_triggered or status.threshold_100_triggered:
                alert = BudgetAlert(
                    alert_id=f"{status.budget_id}_{threshold_percent}",
                    budget_id=status.budget_id,
                    department_name=status.department_name,
                    threshold_percent=threshold_percent,
                    utilization_percent=status.utilization_percent,
                    amount_spent=status.spent_amount,
                    amount_budgeted=status.budgeted_amount,
                    alert_level=alert_level,
                    triggered_at=datetime.utcnow()
                )

                state.alerts.append(alert)
                state.alert_count += 1
                logger.info(f"Alert: {status.department_name} - {alert_level}")

        logger.info(f"Generated {state.alert_count} alerts")
        return state

    async def _aggregate(self, state: BudgetMonitoringState) -> BudgetMonitoringState:
        """Aggregate metrics across all budgets."""
        logger.info("Aggregating metrics")

        if state.budget_statuses:
            state.total_budgeted = sum(s.budgeted_amount for s in state.budget_statuses)
            state.total_spent = sum(s.spent_amount for s in state.budget_statuses)

            if state.total_budgeted > 0:
                state.overall_utilization_percent = (
                    state.total_spent / state.total_budgeted * 100
                )

        logger.info(f"Total: ${state.total_spent} / ${state.total_budgeted} ({state.overall_utilization_percent}%)")
        return state

    async def _report(self, state: BudgetMonitoringState) -> BudgetMonitoringState:
        """Generate final report."""
        logger.info("Generating budget report")
        logger.info(f"""
Budget Report (FY {state.fiscal_year}):
  Departments: {len(state.budget_statuses)}
  Total Budgeted: ${state.total_budgeted}
  Total Spent: ${state.total_spent}
  Overall Utilization: {state.overall_utilization_percent}%
  Active Alerts: {state.alert_count}
        """)
        return state

    async def run(
        self,
        company_id: str,
        fiscal_year: int,
        quarter: int | None = None
    ) -> dict[str, Any]:
        """Execute the budget monitoring."""
        logger.info(f"Starting budget monitoring for {company_id}")

        state = BudgetMonitoringState(
            company_id=company_id,
            fiscal_year=fiscal_year,
            quarter=quarter
        )

        runnable = self.graph.compile()
        final_state = await runnable.ainvoke(state)

        return {
            "success": len(final_state.errors) == 0,
            "fiscal_year": final_state.fiscal_year,
            "quarter": final_state.quarter,
            "total_budgeted": float(final_state.total_budgeted),
            "total_spent": float(final_state.total_spent),
            "overall_utilization_percent": float(final_state.overall_utilization_percent),
            "budgets": [
                {
                    "budget_id": s.budget_id,
                    "department_id": s.department_id,
                    "department_name": s.department_name,
                    "budgeted_amount": float(s.budgeted_amount),
                    "spent_amount": float(s.spent_amount),
                    "remaining_amount": float(s.remaining_amount),
                    "utilization_percent": float(s.utilization_percent),
                    "threshold_80_triggered": s.threshold_80_triggered,
                    "threshold_90_triggered": s.threshold_90_triggered,
                    "threshold_100_triggered": s.threshold_100_triggered,
                }
                for s in final_state.budget_statuses
            ],
            "active_alerts": [
                {
                    "alert_id": a.alert_id,
                    "budget_id": a.budget_id,
                    "department_name": a.department_name,
                    "threshold_percent": a.threshold_percent,
                    "utilization_percent": float(a.utilization_percent),
                    "amount_spent": float(a.amount_spent),
                    "amount_budgeted": float(a.amount_budgeted),
                    "alert_level": a.alert_level,
                    "triggered_at": a.triggered_at.isoformat(),
                }
                for a in final_state.alerts
            ],
            "alert_count": final_state.alert_count,
            "errors": final_state.errors if final_state.errors else None,
        }
