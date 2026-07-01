import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import String, ForeignKey, DateTime, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base


class ForecastModel(Base):
    __tablename__ = "forecasts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False, index=True)

    forecast_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    period: Mapped[str] = mapped_column(String(50), nullable=False)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    forecasted_value: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)

    actual_value: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    variance: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)

    confidence_level: Mapped[int | None] = mapped_column(nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self) -> str:
        return f"<ForecastModel(id={self.id}, forecast_type={self.forecast_type}, period={self.period})>"
