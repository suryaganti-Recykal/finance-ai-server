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
