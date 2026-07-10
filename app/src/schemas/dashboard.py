from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class KPICardSchema(BaseModel):
    label: str
    value: Decimal
    currency: str = "USD"
    change_percent: Decimal | None = None
    change_direction: str | None = None
    target: Decimal | None = None


class TrendPointSchema(BaseModel):
    date: datetime
    value: Decimal


class TrendSchema(BaseModel):
    label: str
    data: list[TrendPointSchema]
    currency: str = "USD"


class DashboardSummarySchema(BaseModel):
    period_start: datetime
    period_end: datetime
    kpis: dict[str, KPICardSchema]


class TrendsSchema(BaseModel):
    revenue_trend: TrendSchema
    expense_trend: TrendSchema
    collections_trend: TrendSchema


class DepartmentSpendSchema(BaseModel):
    department_name: str
    amount: Decimal
    percentage: Decimal


class BudgetUtilizationSchema(BaseModel):
    department_name: str
    budgeted: Decimal
    spent: Decimal
    utilization_percent: Decimal


class CampaignSpendSchema(BaseModel):
    name: str
    platform: str
    spend: Decimal
    leads: int
    purchases: int
    cpl: Decimal
    cpc: Decimal | None = None


class DepartmentSpendBreakdownSchema(BaseModel):
    data: list[DepartmentSpendSchema]


class BudgetUtilizationBreakdownSchema(BaseModel):
    data: list[BudgetUtilizationSchema]


class CampaignSpendBreakdownSchema(BaseModel):
    data: list[CampaignSpendSchema]


# Enhanced schemas for presentation UI
class HealthIndicator(BaseModel):
    """Health status for a metric."""

    status: str  # "healthy", "warning", "critical"
    message: str
    percentage: Decimal | None = None


class ExpenseBreakdown(BaseModel):
    """Expense breakdown by category."""

    category: str
    amount: Decimal
    percentage: float
    transaction_count: int
    trend: str  # "up", "down", "stable"


class BudgetSummary(BaseModel):
    """Department budget summary."""

    department: str
    q1: Decimal
    q2: Decimal
    q3: Decimal
    q4: Decimal
    total: Decimal
    spent: Decimal
    remaining: Decimal
    health: HealthIndicator


class EnhancedDashboard(BaseModel):
    """Complete dashboard data for UI presentation."""

    company_id: str
    timestamp: datetime

    # Summary metrics
    total_expenses: Decimal
    total_revenue: Decimal
    net_profit: Decimal
    budget_utilization: float

    # Breakdowns
    expense_breakdown: list[ExpenseBreakdown]
    budget_summary: list[BudgetSummary]
    top_campaigns: list[CampaignSpendSchema]

    # Health indicators
    overall_health: HealthIndicator
    budget_health: HealthIndicator
    expense_health: HealthIndicator

    # Trends
    revenue_trend: list[TrendPointSchema]
    expense_trend: list[TrendPointSchema]
    budget_trend: list[TrendPointSchema]
