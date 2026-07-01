import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.expenses.services.sync_service import ExpenseSyncService, SyncResult
from src.application.shared.use_case import UseCase
from src.infrastructure.connectors import (
    BankCSVConnector,
    CreditCardConnector,
    GoogleAdsConnector,
    MetaConnector,
    RazorpayConnector,
    ZohoConnector,
)
from src.infrastructure.db.models.expense import ExpenseModel


@dataclass(kw_only=True)
class SyncExpensesInput:
    company_id: uuid.UUID
    start_date: datetime | None = None
    end_date: datetime | None = None


@dataclass(kw_only=True)
class SyncExpensesOutput:
    total_synced: int
    total_duplicates: int
    errors: list[str]
    sync_started_at: datetime
    sync_completed_at: datetime


class SyncExpensesUseCase(UseCase[SyncExpensesInput, SyncExpensesOutput]):
    """Sync expenses from all configured sources (Zoho, Meta, Google Ads, Razorpay, Bank, CC)."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def execute(self, input_data: SyncExpensesInput) -> SyncExpensesOutput:
        now = datetime.now(timezone.utc)
        end_date = input_data.end_date or now
        start_date = input_data.start_date or (now - timedelta(days=30))

        # Initialize all connectors
        connectors = [
            ZohoConnector(),
            MetaConnector(),
            GoogleAdsConnector(),
            RazorpayConnector(),
            # TODO: Add BankCSVConnector and CreditCardConnector when files are provided
        ]

        # Sync from all sources
        sync_service = ExpenseSyncService(connectors)
        transactions, sync_result = await sync_service.sync_expenses(
            input_data.company_id, start_date, end_date
        )

        # Write to database (skip if already exists by source_transaction_id)
        for tx in transactions:
            try:
                expense = ExpenseModel(
                    id=uuid.uuid4(),
                    company_id=input_data.company_id,
                    amount=tx.amount,
                    currency=tx.currency,
                    category=tx.category,
                    description=tx.description,
                    source=tx.source,
                    source_transaction_id=tx.source_transaction_id,
                    expense_date=tx.transaction_date,
                    is_duplicate=False,
                    is_anomalous=False,
                )
                self.db.add(expense)
            except Exception as e:
                sync_result.errors.append(f"Failed to write expense: {str(e)}")

        try:
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            sync_result.errors.append(f"Database commit failed: {str(e)}")

        return SyncExpensesOutput(
            total_synced=sync_result.total_stored,
            total_duplicates=sync_result.total_fetched - sync_result.total_deduplicated,
            errors=sync_result.errors,
            sync_started_at=sync_result.started_at,
            sync_completed_at=sync_result.ended_at,
        )
