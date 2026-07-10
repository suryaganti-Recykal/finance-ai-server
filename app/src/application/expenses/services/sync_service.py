import uuid
from dataclasses import dataclass, field
from datetime import datetime

from src.infrastructure.connectors.base import Connector, ConnectorError, Transaction


@dataclass(kw_only=True)
class SyncResult:
    """Summary of an expense sync run."""

    company_id: uuid.UUID
    started_at: datetime
    ended_at: datetime
    total_fetched: int
    total_deduplicated: int
    total_categorized: int
    total_stored: int
    errors: list[str] = field(default_factory=list)


class ExpenseSyncService:
    """Orchestrates fetching, deduplicating, and categorizing expenses from all sources."""

    def __init__(self, connectors: list[Connector]) -> None:
        self.connectors = connectors

    async def sync_expenses(
        self, company_id: uuid.UUID, start_date: datetime, end_date: datetime
    ) -> tuple[list[Transaction], SyncResult]:
        """Fetch from all connectors, deduplicate, categorize, and return normalized expenses.

        Returns:
            (list of deduplicated transactions, sync result summary)
        """
        started_at = datetime.utcnow()
        all_transactions: list[Transaction] = []
        errors: list[str] = []

        # Fetch from all connectors in parallel (could use asyncio.gather)
        for connector in self.connectors:
            try:
                source = await connector.get_source_name()
                await connector.authenticate()
                transactions = await connector.fetch_transactions(company_id, start_date, end_date)
                all_transactions.extend(transactions)
            except ConnectorError as e:
                errors.append(f"{source or 'Unknown'}: {str(e)}")
            except Exception as e:
                errors.append(f"Unexpected error: {str(e)}")

        # Deduplication: keep first occurrence by (source, source_transaction_id)
        seen: dict[tuple[str, str], int] = {}
        deduplicated: list[Transaction] = []
        duplicates_count = 0

        for tx in all_transactions:
            key = (tx.source, tx.source_transaction_id)
            if key not in seen:
                seen[key] = len(deduplicated)
                deduplicated.append(tx)
            else:
                duplicates_count += 1

        # Categorization: assign category based on keywords/rules (placeholder)
        categorized = self._categorize_expenses(deduplicated)

        ended_at = datetime.utcnow()
        result = SyncResult(
            company_id=company_id,
            started_at=started_at,
            ended_at=ended_at,
            total_fetched=len(all_transactions),
            total_deduplicated=len(deduplicated),
            total_categorized=len(categorized),
            total_stored=len(categorized),  # Will be updated after DB write
            errors=errors,
        )

        return categorized, result

    def _categorize_expenses(self, transactions: list[Transaction]) -> list[Transaction]:
        """Assign categories based on merchant/description keywords.

        This is a simple rule-based categorizer. In production, could use ML.
        """
        category_keywords = {
            "marketing": ["facebook", "google", "meta", "ads", "adspend"],
            "operations": ["aws", "server", "hosting", "infrastructure"],
            "hr": ["salary", "payroll", "employee", "hr"],
            "travel": ["flight", "hotel", "taxi", "airline"],
            "meals": ["restaurant", "coffee", "food", "lunch"],
            "office": ["furniture", "supplies", "desk"],
        }

        for tx in transactions:
            if tx.category and tx.category != "uncategorized":
                continue

            description_lower = (tx.description or "").lower()
            merchant_lower = (tx.merchant or "").lower()
            search_text = f"{description_lower} {merchant_lower}"

            for category, keywords in category_keywords.items():
                if any(kw in search_text for kw in keywords):
                    tx.category = category
                    break

            if tx.category == "uncategorized":
                tx.category = "other"

        return transactions
