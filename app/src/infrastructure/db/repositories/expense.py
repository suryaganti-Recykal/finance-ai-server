"""Expense repository for database operations."""

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.models.expense import ExpenseModel


class ExpenseRepositoryImpl:
    """Repository for expense operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def sum_by_department(
        self,
        company_id: str,
        department_id: str,
        fiscal_year: int,
        quarter: int | None = None
    ) -> Decimal:
        """Get total expenses for a department in a fiscal period."""
        query = select(func.sum(ExpenseModel.amount)).where(
            ExpenseModel.company_id == company_id,
            ExpenseModel.department_id == department_id,
        )

        result = await self.db.execute(query)
        total = result.scalar() or Decimal(0)
        return Decimal(str(total))

    async def create_many_with_category(
        self,
        company_id: str,
        transactions: list,
        categories: list[str]
    ) -> int:
        """Create multiple expenses with categories."""
        for tx, category in zip(transactions, categories):
            expense = ExpenseModel(
                company_id=company_id,
                source=tx.source,
                source_transaction_id=tx.source_transaction_id,
                amount=tx.amount,
                description=tx.description,
                date=tx.transaction_date,
                category=category,
            )
            self.db.add(expense)

        await self.db.commit()
        return len(transactions)
