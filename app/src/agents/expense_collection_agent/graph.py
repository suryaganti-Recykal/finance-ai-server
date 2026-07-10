"""LangGraph agent for expense collection from multiple sources.

Workflow:
1. Fetch: Parallel fetch from 6 sources (Zoho, Meta, Google Ads, Razorpay, Bank, CC)
2. Deduplicate: Remove duplicates by (source, source_transaction_id)
3. Categorize: Assign categories by keyword matching
4. Validate: Check for errors and invalid data
5. Store: Write deduplicated, categorized expenses to database
6. Report: Return summary with counts and errors
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, cast

from langgraph.graph import END, StateGraph

from src.application.expenses.services.sync_service import ExpenseSyncService
from src.core.config.settings import get_settings
from src.core.logging.logger import get_logger
from src.infrastructure.connectors.bank_csv import BankCSVConnector
from src.infrastructure.connectors.base import ConnectorError, Transaction
from src.infrastructure.connectors.credit_card import CreditCardConnector
from src.infrastructure.connectors.google_ads import GoogleAdsConnector
from src.infrastructure.connectors.meta import MetaConnector
from src.infrastructure.connectors.razorpay import RazorpayConnector
from src.infrastructure.connectors.zoho import ZohoConnector
from src.infrastructure.db.repositories.expense import ExpenseRepositoryImpl
from src.infrastructure.db.session import AsyncSession
from src.infrastructure.demo_data import generate_demo_expenses

logger = get_logger(__name__)


@dataclass
class ExpenseCollectionState:
    """State for expense collection workflow."""
    company_id: str
    start_date: datetime
    end_date: datetime

    # Intermediate results
    raw_transactions: list[Transaction] = field(default_factory=list)
    deduplicated_transactions: list[Transaction] = field(default_factory=list)
    categorized_transactions: list[dict[str, Any]] = field(default_factory=list)

    # Tracking
    errors: list[str] = field(default_factory=list)
    connector_results: dict[str, dict] = field(default_factory=dict)

    # Final summary
    total_synced: int = 0
    duplicates_removed: int = 0
    errors_count: int = 0


class ExpenseCollectionGraph:
    """LangGraph implementation of expense collection workflow."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.graph = StateGraph(ExpenseCollectionState)
        self.sync_service = ExpenseSyncService()
        self.expense_repo = ExpenseRepositoryImpl(db)
        self._build_graph()

    def _build_graph(self) -> None:
        """Build the LangGraph workflow."""
        # Add nodes
        self.graph.add_node("fetch", self._fetch_all_sources)
        self.graph.add_node("deduplicate", self._deduplicate)
        self.graph.add_node("categorize", self._categorize)
        self.graph.add_node("validate", self._validate)
        self.graph.add_node("store", self._store)
        self.graph.add_node("report", self._report)

        # Define flow
        self.graph.set_entry_point("fetch")
        self.graph.add_edge("fetch", "deduplicate")
        self.graph.add_edge("deduplicate", "categorize")
        self.graph.add_edge("categorize", "validate")
        self.graph.add_edge("validate", "store")
        self.graph.add_edge("store", "report")
        self.graph.add_edge("report", END)

    async def _fetch_all_sources(self, state: ExpenseCollectionState) -> ExpenseCollectionState:
        """Fetch transactions from all 6 sources in parallel."""
        logger.info(f"Fetching expenses for company {state.company_id}")
        settings = get_settings()

        # Demo/Presentation mode: use sample data
        if settings.USE_SHEETS_FOR_DEMO:
            logger.info("Using demo data (presentation mode)")
            all_transactions = generate_demo_expenses(state.company_id)
            state.connector_results["DemoDataGenerator"] = {
                "count": len(all_transactions),
                "status": "success",
                "note": "Demo/presentation mode"
            }
            state.raw_transactions = all_transactions
            logger.info(f"Total demo transactions loaded: {len(all_transactions)}")
            return state

        # Production mode: use real connectors
        connectors = [
            ZohoConnector(),
            MetaConnector(),
            GoogleAdsConnector(),
            RazorpayConnector(),
            BankCSVConnector(),
            CreditCardConnector(),
        ]

        all_transactions = []

        for connector in connectors:
            try:
                logger.info(f"Fetching from {connector.__class__.__name__}")
                await connector.authenticate()
                transactions = await connector.fetch_transactions(
                    state.company_id,
                    state.start_date,
                    state.end_date
                )

                connector_name = connector.__class__.__name__
                state.connector_results[connector_name] = {
                    "count": len(transactions),
                    "status": "success"
                }

                all_transactions.extend(transactions)
                logger.info(f"{connector_name}: {len(transactions)} transactions")

            except ConnectorError as e:
                logger.error(f"Error fetching from {connector.__class__.__name__}: {e}")
                state.errors.append(f"{connector.__class__.__name__}: {str(e)}")
                state.connector_results[connector.__class__.__name__] = {
                    "count": 0,
                    "status": "error",
                    "error": str(e)
                }
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                state.errors.append(f"Unexpected: {str(e)}")

        state.raw_transactions = all_transactions
        logger.info(f"Total transactions fetched: {len(all_transactions)}")
        return state

    async def _deduplicate(self, state: ExpenseCollectionState) -> ExpenseCollectionState:
        """Remove duplicate transactions by (source, source_transaction_id)."""
        logger.info("Deduplicating transactions")

        seen = set()
        unique_transactions = []

        for tx in state.raw_transactions:
            key = (tx.source, tx.source_transaction_id)
            if key not in seen:
                seen.add(key)
                unique_transactions.append(tx)

        state.duplicates_removed = len(state.raw_transactions) - len(unique_transactions)
        state.deduplicated_transactions = unique_transactions

        logger.info(f"Duplicates removed: {state.duplicates_removed}")
        logger.info(f"Unique transactions: {len(unique_transactions)}")
        return state

    async def _categorize(self, state: ExpenseCollectionState) -> ExpenseCollectionState:
        """Categorize transactions by keyword matching."""
        logger.info("Categorizing transactions")

        keywords = {
            "MARKETING": [
                "facebook", "meta", "google ads", "instagram", "tiktok",
                "advertising", "ads", "campaign", "promotional"
            ],
            "OPERATIONS": [
                "office", "supplies", "software", "tools", "equipment",
                "maintenance", "utilities", "rent", "hosting"
            ],
            "HR": [
                "salary", "payroll", "benefits", "insurance", "recruitment",
                "training", "employee"
            ],
            "SALES": [
                "commission", "travel", "entertainment", "client", "business development"
            ],
        }

        for tx in state.deduplicated_transactions:
            desc_lower = tx.description.lower()
            category = "MISCELLANEOUS"

            for cat, words in keywords.items():
                if any(word in desc_lower for word in words):
                    category = cat
                    break

            state.categorized_transactions.append({
                "source": tx.source,
                "source_transaction_id": tx.source_transaction_id,
                "amount": tx.amount,
                "description": tx.description,
                "date": tx.transaction_date,
                "category": category,
            })

        logger.info(f"Categorized: {len(state.categorized_transactions)} transactions")
        return state

    async def _validate(self, state: ExpenseCollectionState) -> ExpenseCollectionState:
        """Validate transactions for errors."""
        logger.info("Validating transactions")

        valid = []
        for tx in state.categorized_transactions:
            # Check required fields
            if not all([tx.get("source"), tx.get("amount"), tx.get("date")]):
                state.errors.append(f"Invalid transaction: missing fields {tx}")
                state.errors_count += 1
                continue

            # Check amount is positive
            if tx["amount"] <= 0:
                state.errors.append(f"Invalid amount: {tx['amount']}")
                state.errors_count += 1
                continue

            valid.append(tx)

        state.categorized_transactions = valid
        logger.info(f"Valid transactions: {len(valid)}, Invalid: {state.errors_count}")
        return state

    async def _store(self, state: ExpenseCollectionState) -> ExpenseCollectionState:
        """Store transactions in database."""
        logger.info(f"Storing {len(state.categorized_transactions)} transactions")

        try:
            # Convert to Transaction objects for repo
            transactions = [
                Transaction(
                    source=tx["source"],
                    source_transaction_id=tx["source_transaction_id"],
                    amount=Decimal(str(tx["amount"])),
                    description=tx["description"],
                    transaction_date=tx["date"]
                )
                for tx in state.categorized_transactions
            ]

            # Store in database
            saved = await self.expense_repo.create_many_with_category(
                state.company_id,
                transactions,
                [tx["category"] for tx in state.categorized_transactions]
            )

            state.total_synced = saved
            logger.info(f"Stored: {saved} transactions")

        except Exception as e:
            logger.error(f"Error storing transactions: {e}")
            state.errors.append(f"Storage error: {str(e)}")
            state.errors_count += 1

        return state

    async def _report(self, state: ExpenseCollectionState) -> ExpenseCollectionState:
        """Generate final report."""
        logger.info("Generating report")

        logger.info(f"""
Expense Collection Summary:
  Total Synced: {state.total_synced}
  Duplicates Removed: {state.duplicates_removed}
  Errors: {state.errors_count}
  Sources:
{chr(10).join(f'    {k}: {v}' for k, v in state.connector_results.items())}
        """)

        return state

    async def run(
        self,
        company_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> dict[str, Any]:
        """Execute the expense collection workflow."""
        logger.info(f"Starting expense collection for {company_id}")

        state = ExpenseCollectionState(
            company_id=company_id,
            start_date=start_date,
            end_date=end_date
        )

        # Compile graph
        runnable = self.graph.compile()

        # Execute
        final_state = cast(dict[str, Any], await runnable.ainvoke(state))

        return {
            "success": final_state["errors_count"] == 0,
            "total_synced": final_state["total_synced"],
            "duplicates_removed": final_state["duplicates_removed"],
            "errors": final_state["errors_count"],
            "connector_results": final_state["connector_results"],
            "error_details": final_state["errors"] if final_state["errors"] else None,
        }
