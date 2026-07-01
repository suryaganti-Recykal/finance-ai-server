from datetime import datetime

from src.core.config.settings import get_settings
from src.infrastructure.connectors.base import Connector, ConnectorError, Transaction


class RazorpayConnector(Connector):
    """Fetches payments from Razorpay."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = None

    async def authenticate(self) -> None:
        """Authenticate with Razorpay API."""
        if not self.settings.RAZORPAY_KEY_ID:
            raise ConnectorError("Razorpay credentials not configured.")
        # TODO: Initialize Razorpay client
        pass

    async def fetch_transactions(
        self, start_date: datetime, end_date: datetime
    ) -> list[Transaction]:
        """Fetch payments/payouts from Razorpay."""
        # TODO: Call Razorpay API
        return []

    async def get_source_name(self) -> str:
        return "Razorpay"
