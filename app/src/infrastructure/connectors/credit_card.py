import csv
from datetime import datetime
from io import StringIO

from src.infrastructure.connectors.base import Connector, ConnectorError, Transaction


class CreditCardConnector(Connector):
    """Parses credit card statements from CSV files."""

    def __init__(self, csv_content: str, card_name: str = "Credit Card") -> None:
        self.csv_content = csv_content
        self.card_name = card_name

    async def authenticate(self) -> None:
        """No authentication needed for file-based parsing."""
        pass

    async def fetch_transactions(
        self, start_date: datetime, end_date: datetime
    ) -> list[Transaction]:
        """Parse CSV and extract transactions.

        Expected CSV columns: Date, Merchant, Amount, Category
        """
        transactions = []
        try:
            reader = csv.DictReader(StringIO(self.csv_content))
            for row in reader:
                if not row:
                    continue
                # TODO: Parse row and normalize to Transaction
                # For now, return empty
                pass
        except Exception as e:
            raise ConnectorError(f"Failed to parse credit card CSV: {e}") from e
        return transactions

    async def get_source_name(self) -> str:
        return f"Credit Card ({self.card_name})"
