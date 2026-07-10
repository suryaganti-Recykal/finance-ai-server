from decimal import Decimal

from pydantic import BaseModel


class BudgetStatusSchema(BaseModel):
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


class BudgetAlertSchema(BaseModel):
    alert_id: str
    budget_id: str
    department_name: str
    threshold_percent: int
    utilization_percent: Decimal
    amount_spent: Decimal
    amount_budgeted: Decimal
    alert_level: str
    triggered_at: str


class BudgetSummarySchema(BaseModel):
    fiscal_year: int
    quarter: int | None
    total_budgeted: Decimal
    total_spent: Decimal
    overall_utilization_percent: Decimal
    budgets: list[BudgetStatusSchema]
    active_alerts: list[BudgetAlertSchema]
