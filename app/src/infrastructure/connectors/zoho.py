from datetime import datetime

from src.core.config.settings import get_settings
from src.infrastructure.connectors.base import Connector, ConnectorError, Transaction


class ZohoConnector(Connector):
    """Fetches expenses from Zoho Books via API."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = None

    async def authenticate(self) -> None:
        """Authenticate with Zoho Books API."""
        if not self.settings.ZOHO_API_KEY:
            raise ConnectorError("Zoho API key not configured.")
        # TODO: Initialize Zoho client with API key
        # For now, we skip actual authentication
        pass

    async def fetch_transactions(
        self, company_id: str, start_date: datetime, end_date: datetime
    ) -> list[Transaction]:
        """Fetch expenses from Zoho Books."""
        # TODO: Call Zoho API with date range
        # For now, return empty list (stub)
        return []

    async def get_source_name(self) -> str:
        return "Zoho Books"
