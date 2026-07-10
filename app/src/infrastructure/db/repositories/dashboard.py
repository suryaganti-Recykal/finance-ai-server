import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.dashboard.entities.metrics import (
    BudgetUtilizationBreakdown,
    CampaignSpendBreakdown,
    DepartmentSpendBreakdown,
    Trend,
    TrendPoint,
)
from src.domain.dashboard.repositories.dashboard import DashboardRepository
from src.infrastructure.db.models.budget import BudgetModel
from src.infrastructure.db.models.campaign import CampaignModel
from src.infrastructure.db.models.collections import CollectionModel
from src.infrastructure.db.models.department import DepartmentModel
from src.infrastructure.db.models.expense import ExpenseModel
from src.infrastructure.db.models.invoice import InvoiceModel
from src.infrastructure.db.models.revenue import RevenueModel


class DashboardRepositoryImpl(DashboardRepository):
    """SQLAlchemy-based dashboard data aggregation."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_total_revenue(
        self, company_id: uuid.UUID, start_date: datetime, end_date: datetime
    ) -> Decimal:
        stmt = select(func.coalesce(func.sum(RevenueModel.amount), Decimal(0))).where(
            RevenueModel.company_id == company_id,
            RevenueModel.revenue_date >= start_date,
            RevenueModel.revenue_date <= end_date,
        )
        result = await self._session.execute(stmt)
        return result.scalar()

    async def get_total_expenses(
        self, company_id: uuid.UUID, start_date: datetime, end_date: datetime
    ) -> Decimal:
        stmt = select(func.coalesce(func.sum(ExpenseModel.amount), Decimal(0))).where(
            ExpenseModel.company_id == company_id,
            ExpenseModel.expense_date >= start_date,
            ExpenseModel.expense_date <= end_date,
        )
        result = await self._session.execute(stmt)
        return result.scalar()

    async def get_total_collections(
        self, company_id: uuid.UUID, start_date: datetime, end_date: datetime
    ) -> Decimal:
        stmt = select(func.coalesce(func.sum(CollectionModel.amount), Decimal(0))).where(
            CollectionModel.company_id == company_id,
            CollectionModel.collection_date >= start_date,
            CollectionModel.collection_date <= end_date,
        )
        result = await self._session.execute(stmt)
        return result.scalar()

    async def get_total_marketing_spend(
        self, company_id: uuid.UUID, start_date: datetime, end_date: datetime
    ) -> Decimal:
        stmt = select(func.coalesce(func.sum(CampaignModel.total_spend), Decimal(0))).where(
            CampaignModel.company_id == company_id,
            CampaignModel.start_date >= start_date,
            CampaignModel.start_date <= end_date,
        )
        result = await self._session.execute(stmt)
        return result.scalar()

    async def get_outstanding_receivables(self, company_id: uuid.UUID) -> Decimal:
        stmt = select(func.coalesce(func.sum(InvoiceModel.amount), Decimal(0))).where(
            InvoiceModel.company_id == company_id,
            InvoiceModel.status.in_(["sent", "viewed", "overdue"]),
        )
        result = await self._session.execute(stmt)
        return result.scalar()

    async def get_outstanding_payables(self, company_id: uuid.UUID) -> Decimal:
        return Decimal(0)

    async def get_cash_balance(self, company_id: uuid.UUID) -> Decimal | None:
        return None

    async def get_revenue_trend(
        self, company_id: uuid.UUID, start_date: datetime, end_date: datetime, period: str = "daily"
    ) -> Trend:
        stmt = select(
            func.date(RevenueModel.revenue_date).label("date"),
            func.sum(RevenueModel.amount).label("amount"),
        ).where(
            RevenueModel.company_id == company_id,
            RevenueModel.revenue_date >= start_date,
            RevenueModel.revenue_date <= end_date,
        ).group_by(
            func.date(RevenueModel.revenue_date)
        ).order_by(
            "date"
        )
        result = await self._session.execute(stmt)
        rows = result.fetchall()
        data = [TrendPoint(date=row[0], value=row[1]) for row in rows]
        return Trend(label="Revenue", data=data)

    async def get_expense_trend(
        self, company_id: uuid.UUID, start_date: datetime, end_date: datetime, period: str = "daily"
    ) -> Trend:
        stmt = select(
            func.date(ExpenseModel.expense_date).label("date"),
            func.sum(ExpenseModel.amount).label("amount"),
        ).where(
            ExpenseModel.company_id == company_id,
            ExpenseModel.expense_date >= start_date,
            ExpenseModel.expense_date <= end_date,
        ).group_by(
            func.date(ExpenseModel.expense_date)
        ).order_by(
            "date"
        )
        result = await self._session.execute(stmt)
        rows = result.fetchall()
        data = [TrendPoint(date=row[0], value=row[1]) for row in rows]
        return Trend(label="Expenses", data=data)

    async def get_collections_trend(
        self, company_id: uuid.UUID, start_date: datetime, end_date: datetime, period: str = "daily"
    ) -> Trend:
        stmt = select(
            func.date(CollectionModel.collection_date).label("date"),
            func.sum(CollectionModel.amount).label("amount"),
        ).where(
            CollectionModel.company_id == company_id,
            CollectionModel.collection_date >= start_date,
            CollectionModel.collection_date <= end_date,
        ).group_by(
            func.date(CollectionModel.collection_date)
        ).order_by(
            "date"
        )
        result = await self._session.execute(stmt)
        rows = result.fetchall()
        data = [TrendPoint(date=row[0], value=row[1]) for row in rows]
        return Trend(label="Collections", data=data)

    async def get_department_spend(
        self, company_id: uuid.UUID, start_date: datetime, end_date: datetime
    ) -> list[DepartmentSpendBreakdown]:
        stmt = select(
            DepartmentModel.name,
            func.sum(ExpenseModel.amount).label("total"),
        ).join(
            ExpenseModel, ExpenseModel.department_id == DepartmentModel.id
        ).where(
            DepartmentModel.company_id == company_id,
            ExpenseModel.expense_date >= start_date,
            ExpenseModel.expense_date <= end_date,
        ).group_by(
            DepartmentModel.id, DepartmentModel.name
        )
        result = await self._session.execute(stmt)
        rows = result.fetchall()
        total_spend = sum(Decimal(row[1]) for row in rows if row[1])
        return [
            DepartmentSpendBreakdown(
                department_name=row[0],
                amount=Decimal(row[1]) or Decimal(0),
                percentage=((Decimal(row[1]) or Decimal(0)) / total_spend * 100) if total_spend else Decimal(0),
            )
            for row in rows
        ]

    async def get_budget_utilization(
        self, company_id: uuid.UUID
    ) -> list[BudgetUtilizationBreakdown]:
        stmt = select(
            DepartmentModel.name,
            BudgetModel.budgeted_amount,
            BudgetModel.spent_amount,
        ).join(
            BudgetModel, BudgetModel.department_id == DepartmentModel.id
        ).where(
            DepartmentModel.company_id == company_id,
            BudgetModel.fiscal_year == datetime.now().year,
        )
        result = await self._session.execute(stmt)
        rows = result.fetchall()
        return [
            BudgetUtilizationBreakdown(
                department_name=row[0],
                budgeted=Decimal(row[1]),
                spent=Decimal(row[2]),
                utilization_percent=(Decimal(row[2]) / Decimal(row[1]) * 100) if row[1] else Decimal(0),
            )
            for row in rows
        ]

    async def get_campaign_spend(
        self, company_id: uuid.UUID, start_date: datetime, end_date: datetime
    ) -> list[CampaignSpendBreakdown]:
        stmt = select(CampaignModel).where(
            CampaignModel.company_id == company_id,
            CampaignModel.start_date >= start_date,
            CampaignModel.start_date <= end_date,
        )
        result = await self._session.execute(stmt)
        campaigns = result.scalars().all()
        return [
            CampaignSpendBreakdown(
                name=c.name,
                platform=c.platform,
                spend=c.total_spend,
                leads=c.leads,
                purchases=c.purchases,
                cpl=(c.total_spend / c.leads) if c.leads > 0 else Decimal(0),
                cpc=(c.total_spend / c.purchases) if c.purchases > 0 else None,
            )
            for c in campaigns
        ]
