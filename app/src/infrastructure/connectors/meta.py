from datetime import datetime

from src.core.config.settings import get_settings
from src.infrastructure.connectors.base import Connector, ConnectorError, Transaction


class MetaConnector(Connector):
    """Fetches ad spend from Meta (Facebook) Ads Manager."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = None

    async def authenticate(self) -> None:
        """Authenticate with Meta Graph API."""
        if not self.settings.META_ACCESS_TOKEN:
            raise ConnectorError("Meta access token not configured.")
        # TODO: Initialize Meta Graph API client
        pass

    async def fetch_transactions(
        self, start_date: datetime, end_date: datetime
    ) -> list[Transaction]:
        """Fetch ad spend from Meta Ads Manager."""
        # TODO: Call Meta Graph API
        return []

    async def get_source_name(self) -> str:
        return "Meta Ads"
