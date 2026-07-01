import uuid
from dataclasses import dataclass
from decimal import Decimal


@dataclass(kw_only=True)
class BudgetStatus:
    """Current status of a department budget."""

    budget_id: uuid.UUID
    department_id: uuid.UUID
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


@dataclass(kw_only=True)
class BudgetAlert:
    """Alert when a budget threshold is crossed."""

    alert_id: uuid.UUID
    budget_id: uuid.UUID
    department_name: str
    threshold_percent: int  # 80, 90, or 100
    utilization_percent: Decimal
    amount_spent: Decimal
    amount_budgeted: Decimal
    alert_level: str  # "warning", "critical"
    triggered_at: str  # ISO datetime
    acknowledged: bool = False


@dataclass(kw_only=True)
class BudgetSummary:
    """Summary of all department budgets."""

    fiscal_year: int
    quarter: int | None
    total_budgeted: Decimal
    total_spent: Decimal
    overall_utilization_percent: Decimal
    budgets: list[BudgetStatus]
    active_alerts: list[BudgetAlert]
