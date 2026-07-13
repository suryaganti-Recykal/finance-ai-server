"""Live connector for Recykal's marketing spend tracker (Google Sheet).

Reads the public CSV export of the sheet — no OAuth needed since the sheet
is shared "Anyone with the link can view". Structure (long format):

    Team, Sub-Team, Segments, Type, Month, Sustainability, Marketplace, DRS, Brand, Total

Each row is one line-item's spend for one month, broken down across four
business units (Sustainability, Marketplace, DRS, Brand).
"""

import csv
import io
from dataclasses import dataclass, field
from datetime import datetime

import httpx

from src.core.logging.logger import get_logger

logger = get_logger(__name__)

BUSINESS_UNITS = ["Sustainability", "Marketplace", "DRS", "Brand"]

# Fiscal year starts in April. Sheet only labels months, not years.
_MONTH_TO_FY_OFFSET = {
    "April": 0, "May": 1, "June": 2, "July": 3, "August": 4, "September": 5,
    "October": 6, "November": 7, "December": 8, "January": 9, "February": 10, "March": 11,
}


@dataclass
class SpendRecord:
    """One line-item's spend for one month."""

    team: str
    sub_team: str
    segment: str
    type: str
    month: str
    business_units: dict[str, float] = field(default_factory=dict)
    total: float = 0.0

    @property
    def date(self) -> datetime:
        """Approximate date (1st of month) using fiscal year starting April."""
        offset = _MONTH_TO_FY_OFFSET.get(self.month, 0)
        fy_start_year = datetime.now().year
        month_num = (3 + offset) % 12 + 1  # April=4 ... March=3
        year = fy_start_year if month_num >= 4 else fy_start_year + 1
        return datetime(year, month_num, 1)


class MarketingSpendSheetConnector:
    """Fetches and parses the live Recykal marketing spend sheet."""

    def __init__(self, sheet_id: str, gid: str):
        self.sheet_id = sheet_id
        self.gid = gid
        self.csv_url = (
            f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
        )

    async def fetch_records(self) -> list[SpendRecord]:
        """Fetch and parse all non-empty spend records from the sheet."""
        async with httpx.AsyncClient() as client:
            response = await client.get(self.csv_url, timeout=15.0, follow_redirects=True)
            response.raise_for_status()
            raw_csv = response.text

        reader = csv.reader(io.StringIO(raw_csv))
        rows = list(reader)

        if not rows:
            logger.warning("Marketing spend sheet returned no rows")
            return []

        records = []
        for row in rows[1:]:  # skip header
            if len(row) < 10:
                continue

            team, sub_team, segment, type_, month = row[0:5]
            month = month.strip()

            if not team or team == "Team":
                continue

            total = self._parse_number(row[9])
            if total == 0:
                continue  # skip empty future months

            business_units = {
                "Sustainability": self._parse_number(row[5]),
                "Marketplace": self._parse_number(row[6]),
                "DRS": self._parse_number(row[7]),
                "Brand": self._parse_number(row[8]),
            }

            records.append(
                SpendRecord(
                    team=team,
                    sub_team=sub_team,
                    segment=segment,
                    type=type_.strip(),
                    month=month,
                    business_units=business_units,
                    total=total,
                )
            )

        logger.info(f"Parsed {len(records)} marketing spend records from live sheet")
        return records

    @staticmethod
    def _parse_number(value: str) -> float:
        if not value or not value.strip():
            return 0.0
        try:
            return float(value.replace(",", "").strip())
        except ValueError:
            return 0.0
