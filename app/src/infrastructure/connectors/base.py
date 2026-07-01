from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(kw_only=True)
class Transaction:
    """Normalized transaction from any external source (Zoho, Meta, Google Ads, Razorpay, Bank, CC).

    All connectors translate their native format to this schema.
    """

    source: str
    source_transaction_id: str
    amount: Decimal
    currency: str
    category: str
    description: str
    transaction_date: datetime
    merchant: str | None = None
    payment_method: str | None = None
    metadata: dict | None = None


class ConnectorError(Exception):
    """Base error for connector operations."""

    pass


class Connector(ABC):
    """Port for fetching transactions from a data source.

    Each connector (Zoho, Meta, Google Ads, etc.) implements this interface
    to normalize and return transactions. Deduplication, categorization, and
    storage are handled upstream.
    """

    @abstractmethod
    async def authenticate(self) -> None:
        """Authenticate with the external service (OAuth, API key, etc.)."""
        ...

    @abstractmethod
    async def fetch_transactions(
        self, start_date: datetime, end_date: datetime
    ) -> list[Transaction]:
        """Fetch transactions for the given date range.

        Returns a list of normalized Transaction objects.
        Raises ConnectorError on auth failure, rate limiting, or service errors.
        """
        ...

    @abstractmethod
    async def get_source_name(self) -> str:
        """Human-readable name of the source (e.g. 'Zoho Books')."""
        ...
