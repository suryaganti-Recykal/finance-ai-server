from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(kw_only=True)
class KPIMetric:
    """A single KPI card (revenue, expenses, profit, etc.)."""

    label: str
    value: Decimal
    currency: str = "USD"
    change_percent: Decimal | None = None
    change_direction: str | None = None  # "up", "down", "stable"
    target: Decimal | None = None  # for budgets
    trend_sparkline: list[Decimal] | None = None


@dataclass(kw_only=True)
class TrendPoint:
    """A single point on a trend line (date, value)."""

    date: datetime
    value: Decimal


@dataclass(kw_only=True)
class Trend:
    """Time-series data for a metric (revenue trend, expense trend, etc.)."""

    label: str
    data: list[TrendPoint]
    currency: str = "USD"


@dataclass(kw_only=True)
class DepartmentSpendBreakdown:
    """Spending by department (for pie chart)."""

    department_name: str
    amount: Decimal
    percentage: Decimal


@dataclass(kw_only=True)
class BudgetUtilizationBreakdown:
    """Budget utilization by department (budgeted vs. spent)."""

    department_name: str
    budgeted: Decimal
    spent: Decimal
    utilization_percent: Decimal


@dataclass(kw_only=True)
class CampaignSpendBreakdown:
    """Marketing spend by platform/campaign."""

    name: str
    platform: str
    spend: Decimal
    leads: int
    purchases: int
    cpl: Decimal  # cost per lead
    cpc: Decimal | None = None  # cost per purchase
