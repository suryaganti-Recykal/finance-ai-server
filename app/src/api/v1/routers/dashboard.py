from datetime import datetime

from fastapi import APIRouter

from src.api.deps import CurrentCompanyId, DbSession, Pagination
from src.application.dashboard.use_cases.get_dashboard import (
    GetDashboardInput,
    GetDashboardUseCase,
)
from src.application.dashboard.use_cases.get_trends import GetTrendsInput, GetTrendsUseCase
from src.infrastructure.db.repositories.dashboard import DashboardRepositoryImpl
from src.schemas.common import SuccessResponse
from src.schemas.dashboard import (
    BudgetUtilizationBreakdownSchema,
    CampaignSpendBreakdownSchema,
    DashboardSummarySchema,
    DepartmentSpendBreakdownSchema,
    TrendsSchema,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=SuccessResponse[DashboardSummarySchema])
async def get_dashboard(
    company_id: CurrentCompanyId,
    db: DbSession,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> SuccessResponse[DashboardSummarySchema]:
    """Get dashboard KPIs for the given period (defaults to last 30 days)."""
    repo = DashboardRepositoryImpl(db)
    use_case = GetDashboardUseCase(repo)

    result = await use_case.execute(
        GetDashboardInput(company_id=company_id, start_date=start_date, end_date=end_date)
    )

    kpis_dict = {k: v.__dict__ for k, v in result.kpis.items()}
    return SuccessResponse(
        data=DashboardSummarySchema(
            period_start=result.period_start,
            period_end=result.period_end,
            kpis=kpis_dict,
        )
    )


@router.get("/trends", response_model=SuccessResponse[TrendsSchema])
async def get_trends(
    company_id: CurrentCompanyId,
    db: DbSession,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> SuccessResponse[TrendsSchema]:
    """Get historical trends (revenue, expenses, collections) for the given period (defaults to 90 days)."""
    repo = DashboardRepositoryImpl(db)
    use_case = GetTrendsUseCase(repo)

    result = await use_case.execute(
        GetTrendsInput(company_id=company_id, start_date=start_date, end_date=end_date)
    )

    revenue_data = [
        {"date": p.date, "value": p.value} for p in result.revenue_trend.data
    ]
    expense_data = [
        {"date": p.date, "value": p.value} for p in result.expense_trend.data
    ]
    collections_data = [
        {"date": p.date, "value": p.value} for p in result.collections_trend.data
    ]

    return SuccessResponse(
        data=TrendsSchema(
            revenue_trend={
                "label": result.revenue_trend.label,
                "data": revenue_data,
                "currency": result.revenue_trend.currency,
            },
            expense_trend={
                "label": result.expense_trend.label,
                "data": expense_data,
                "currency": result.expense_trend.currency,
            },
            collections_trend={
                "label": result.collections_trend.label,
                "data": collections_data,
                "currency": result.collections_trend.currency,
            },
        )
    )


@router.get("/department-spend", response_model=SuccessResponse[DepartmentSpendBreakdownSchema])
async def get_department_spend(
    company_id: CurrentCompanyId,
    db: DbSession,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> SuccessResponse[DepartmentSpendBreakdownSchema]:
    """Get spending breakdown by department (pie chart data)."""
    repo = DashboardRepositoryImpl(db)
    result = await repo.get_department_spend(company_id, start_date, end_date)

    data = [
        {
            "department_name": item.department_name,
            "amount": item.amount,
            "percentage": item.percentage,
        }
        for item in result
    ]

    return SuccessResponse(data=DepartmentSpendBreakdownSchema(data=data))


@router.get("/budget-utilization", response_model=SuccessResponse[BudgetUtilizationBreakdownSchema])
async def get_budget_utilization(
    company_id: CurrentCompanyId,
    db: DbSession,
) -> SuccessResponse[BudgetUtilizationBreakdownSchema]:
    """Get budget utilization by department."""
    repo = DashboardRepositoryImpl(db)
    result = await repo.get_budget_utilization(company_id)

    data = [
        {
            "department_name": item.department_name,
            "budgeted": item.budgeted,
            "spent": item.spent,
            "utilization_percent": item.utilization_percent,
        }
        for item in result
    ]

    return SuccessResponse(data=BudgetUtilizationBreakdownSchema(data=data))


@router.get("/campaigns", response_model=SuccessResponse[CampaignSpendBreakdownSchema])
async def get_campaign_spend(
    company_id: CurrentCompanyId,
    db: DbSession,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> SuccessResponse[CampaignSpendBreakdownSchema]:
    """Get marketing campaign spend breakdown."""
    repo = DashboardRepositoryImpl(db)
    result = await repo.get_campaign_spend(company_id, start_date, end_date)

    data = [
        {
            "name": item.name,
            "platform": item.platform,
            "spend": item.spend,
            "leads": item.leads,
            "purchases": item.purchases,
            "cpl": item.cpl,
            "cpc": item.cpc,
        }
        for item in result
    ]

    return SuccessResponse(data=CampaignSpendBreakdownSchema(data=data))
