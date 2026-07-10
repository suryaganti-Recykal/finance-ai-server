"""Google Sheets connector for pulling demo data.

Supports OAuth2 authentication and reads from multiple named sheets.
Easily swappable with actual API connectors later.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any

import httpx

from src.core.logging.logger import get_logger
from src.infrastructure.connectors.base import Connector, ConnectorError, Transaction

logger = get_logger(__name__)


class GoogleSheetsConnector(Connector):
    """Fetches transactions from Google Sheets using Sheets API v4.

    For presentation: reads demo data. Later swap for real API calls.
    """

    def __init__(self, sheet_id: str, oauth_token: str | None = None):
        self.sheet_id = sheet_id
        self.oauth_token = oauth_token
        self.authenticated = False

    async def authenticate(self) -> None:
        """Verify credentials work. For OAuth, token should be pre-validated."""
        if not self.oauth_token:
            raise ConnectorError("No OAuth token provided. User must login first.")
        self.authenticated = True
        logger.info(f"Google Sheets authenticated for sheet {self.sheet_id}")

    async def fetch_transactions(
        self, company_id: str, start_date: datetime, end_date: datetime
    ) -> list[Transaction]:
        """Fetch transactions from 'Expenses' sheet.

        Sheet columns: Date, Description, Amount, Category, Source, MerchantName
        """
        if not self.authenticated:
            raise ConnectorError("Not authenticated. Call authenticate() first.")

        try:
            sheet_data = await self._read_sheet("Expenses")
            transactions = []

            for row in sheet_data:
                if len(row) < 5:
                    continue

                try:
                    tx_date = self._parse_date(row[0])
                    if not (start_date <= tx_date <= end_date):
                        continue

                    amount = Decimal(str(row[2]).replace("$", "").replace(",", ""))
                    transaction = Transaction(
                        source="google_sheets",
                        source_transaction_id=f"{self.sheet_id}_{row[0]}_{row[1][:20]}",
                        amount=amount,
                        currency="USD",
                        category=row[3] if len(row) > 3 else "uncategorized",
                        description=row[1],
                        transaction_date=tx_date,
                        merchant=row[5] if len(row) > 5 else None,
                        metadata={"sheet_id": self.sheet_id, "company_id": company_id},
                    )
                    transactions.append(transaction)
                except (ValueError, IndexError) as e:
                    logger.warning(f"Skipping malformed row: {row} — {e}")

            logger.info(f"Fetched {len(transactions)} transactions from Expenses sheet")
            return transactions

        except Exception as e:
            raise ConnectorError(f"Failed to fetch from Expenses sheet: {str(e)}")

    async def fetch_marketing_campaigns(self, company_id: str) -> list[dict[str, Any]]:
        """Fetch marketing campaign spend from 'Marketing' sheet.

        Sheet columns: CampaignName, Platform, Spend, Impressions, Clicks, Conversions, StartDate
        """
        if not self.authenticated:
            raise ConnectorError("Not authenticated.")

        try:
            sheet_data = await self._read_sheet("Marketing")
            campaigns = []

            for row in sheet_data:
                if len(row) < 5:
                    continue

                try:
                    spend = Decimal(str(row[2]).replace("$", "").replace(",", ""))
                    campaign = {
                        "name": row[0],
                        "platform": row[1],
                        "spend": spend,
                        "impressions": int(row[3]) if len(row) > 3 else 0,
                        "clicks": int(row[4]) if len(row) > 4 else 0,
                        "conversions": int(row[5]) if len(row) > 5 else 0,
                        "start_date": self._parse_date(row[6]) if len(row) > 6 else datetime.now(),
                    }
                    campaigns.append(campaign)
                except (ValueError, IndexError) as e:
                    logger.warning(f"Skipping malformed campaign row: {row} — {e}")

            logger.info(f"Fetched {len(campaigns)} campaigns from Marketing sheet")
            return campaigns

        except Exception as e:
            raise ConnectorError(f"Failed to fetch from Marketing sheet: {str(e)}")

    async def fetch_budgets(self, company_id: str) -> list[dict[str, Any]]:
        """Fetch budget allocations from 'Budgets' sheet.

        Sheet columns: Department, Q1, Q2, Q3, Q4, Total, Status
        """
        if not self.authenticated:
            raise ConnectorError("Not authenticated.")

        try:
            sheet_data = await self._read_sheet("Budgets")
            budgets = []

            for row in sheet_data:
                if len(row) < 3:
                    continue

                try:
                    budget = {
                        "department": row[0],
                        "q1": Decimal(str(row[1]).replace("$", "").replace(",", "")) if len(row) > 1 else Decimal(0),
                        "q2": Decimal(str(row[2]).replace("$", "").replace(",", "")) if len(row) > 2 else Decimal(0),
                        "q3": Decimal(str(row[3]).replace("$", "").replace(",", "")) if len(row) > 3 else Decimal(0),
                        "q4": Decimal(str(row[4]).replace("$", "").replace(",", "")) if len(row) > 4 else Decimal(0),
                        "total": Decimal(str(row[5]).replace("$", "").replace(",", "")) if len(row) > 5 else Decimal(0),
                        "status": row[6] if len(row) > 6 else "active",
                    }
                    budgets.append(budget)
                except (ValueError, IndexError) as e:
                    logger.warning(f"Skipping malformed budget row: {row} — {e}")

            logger.info(f"Fetched {len(budgets)} budget allocations from Budgets sheet")
            return budgets

        except Exception as e:
            raise ConnectorError(f"Failed to fetch from Budgets sheet: {str(e)}")

    async def _read_sheet(self, sheet_name: str) -> list[list[str]]:
        """Read data from a named sheet using Sheets API."""
        if not self.oauth_token:
            raise ConnectorError("No OAuth token available.")

        url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.sheet_id}/values/{sheet_name}"
        headers = {"Authorization": f"Bearer {self.oauth_token}"}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10.0)
            response.raise_for_status()

            data = response.json()
            return data.get("values", [])

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date from various formats."""
        for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%m-%d-%Y"]:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        return datetime.now()

    async def get_source_name(self) -> str:
        """Return human-readable source name."""
        return "Google Sheets (Demo)"
