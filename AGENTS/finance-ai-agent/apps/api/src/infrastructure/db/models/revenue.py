import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import String, ForeignKey, DateTime, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base


class RevenueModel(Base):
    __tablename__ = "revenues"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False, index=True)

    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    revenue_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    source_transaction_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self) -> str:
        return f"<RevenueModel(id={self.id}, amount={self.amount}, source={self.source})>"
