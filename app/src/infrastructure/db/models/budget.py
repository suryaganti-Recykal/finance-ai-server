import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import String, ForeignKey, DateTime, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base


class BudgetModel(Base):
    __tablename__ = "budgets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False, index=True)
    department_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("departments.id"), nullable=False, index=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    budgeted_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    spent_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)

    fiscal_year: Mapped[int] = mapped_column(nullable=False)
    quarter: Mapped[int | None] = mapped_column(nullable=True)

    threshold_80: Mapped[bool] = mapped_column(default=False)
    threshold_90: Mapped[bool] = mapped_column(default=False)
    threshold_100: Mapped[bool] = mapped_column(default=False)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self) -> str:
        return f"<BudgetModel(id={self.id}, department_id={self.department_id}, budgeted={self.budgeted_amount})>"
