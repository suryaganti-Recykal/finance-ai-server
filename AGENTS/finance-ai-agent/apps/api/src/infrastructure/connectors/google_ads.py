from datetime import datetime

from src.core.config.settings import get_settings
from src.infrastructure.connectors.base import Connector, ConnectorError, Transaction


class GoogleAdsConnector(Connector):
    """Fetches ad spend from Google Ads API."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = None

    async def authenticate(self) -> None:
        """Authenticate with Google Ads API."""
        if not self.settings.GOOGLE_ADS_DEVELOPER_TOKEN:
            raise ConnectorError("Google Ads credentials not configured.")
        # TODO: Initialize Google Ads client
        pass

    async def fetch_transactions(
        self, start_date: datetime, end_date: datetime
    ) -> list[Transaction]:
        """Fetch ad spend from Google Ads."""
        # TODO: Call Google Ads API
        return []

    async def get_source_name(self) -> str:
        return "Google Ads"
