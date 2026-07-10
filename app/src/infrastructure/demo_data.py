"""Demo data generator for presentation mode.

Quick-start sample data that agents can use before real APIs are integrated.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

from src.infrastructure.connectors.base import Transaction


def generate_demo_expenses(company_id: str) -> list[Transaction]:
    """Generate sample expense transactions for demo."""
    now = datetime.now()
    base_date = now.replace(day=1)

    transactions = [
        Transaction(
            source="google_sheets_demo",
            source_transaction_id=f"demo_exp_001",
            amount=Decimal("1500"),
            currency="USD",
            category="Operations",
            description="Slack annual subscription",
            transaction_date=base_date + timedelta(days=5),
            merchant="Slack",
            metadata={"company_id": company_id, "demo": True},
        ),
        Transaction(
            source="google_sheets_demo",
            source_transaction_id=f"demo_exp_002",
            amount=Decimal("2500"),
            currency="USD",
            category="Marketing",
            description="Google Ads campaign - Winter Sale",
            transaction_date=base_date + timedelta(days=7),
            merchant="Google Ads",
            metadata={"company_id": company_id, "demo": True},
        ),
        Transaction(
            source="google_sheets_demo",
            source_transaction_id=f"demo_exp_003",
            amount=Decimal("800"),
            currency="USD",
            category="Operations",
            description="AWS hosting and storage",
            transaction_date=base_date + timedelta(days=10),
            merchant="AWS",
            metadata={"company_id": company_id, "demo": True},
        ),
        Transaction(
            source="google_sheets_demo",
            source_transaction_id=f"demo_exp_004",
            amount=Decimal("3000"),
            currency="USD",
            category="Marketing",
            description="Meta Ads campaign - Product Launch",
            transaction_date=base_date + timedelta(days=12),
            merchant="Meta",
            metadata={"company_id": company_id, "demo": True},
        ),
        Transaction(
            source="google_sheets_demo",
            source_transaction_id=f"demo_exp_005",
            amount=Decimal("450"),
            currency="USD",
            category="Operations",
            description="Office supplies and equipment",
            transaction_date=base_date + timedelta(days=15),
            merchant="Staples",
            metadata={"company_id": company_id, "demo": True},
        ),
        Transaction(
            source="google_sheets_demo",
            source_transaction_id=f"demo_exp_006",
            amount=Decimal("1200"),
            currency="USD",
            category="Operations",
            description="HubSpot CRM subscription",
            transaction_date=base_date + timedelta(days=18),
            merchant="HubSpot",
            metadata={"company_id": company_id, "demo": True},
        ),
    ]

    return transactions


def generate_demo_marketing_campaigns(company_id: str) -> list[dict[str, Any]]:
    """Generate sample marketing campaign data."""
    now = datetime.now()
    base_date = now.replace(day=1)

    return [
        {
            "name": "Winter Sale Campaign",
            "platform": "Facebook",
            "spend": Decimal("5000"),
            "impressions": 250000,
            "clicks": 12500,
            "conversions": 750,
            "start_date": base_date,
            "roi": 3.2,
        },
        {
            "name": "Product Launch - Google Ads",
            "platform": "Google Ads",
            "spend": Decimal("7500"),
            "impressions": 450000,
            "clicks": 18000,
            "conversions": 1200,
            "start_date": base_date + timedelta(days=5),
            "roi": 2.8,
        },
        {
            "name": "Retargeting - Meta",
            "platform": "Meta",
            "spend": Decimal("3000"),
            "impressions": 150000,
            "clicks": 8500,
            "conversions": 450,
            "start_date": base_date + timedelta(days=10),
            "roi": 2.5,
        },
        {
            "name": "Email Newsletter",
            "platform": "Email",
            "spend": Decimal("500"),
            "impressions": 25000,
            "clicks": 3500,
            "conversions": 350,
            "start_date": base_date + timedelta(days=1),
            "roi": 4.1,
        },
    ]


def generate_demo_budgets(company_id: str) -> list[dict[str, Any]]:
    """Generate sample budget allocations by department."""
    return [
        {
            "department": "Marketing",
            "q1": Decimal("50000"),
            "q2": Decimal("55000"),
            "q3": Decimal("60000"),
            "q4": Decimal("70000"),
            "total": Decimal("235000"),
            "status": "active",
            "spent": Decimal("15500"),
            "remaining": Decimal("19500"),
        },
        {
            "department": "Operations",
            "q1": Decimal("40000"),
            "q2": Decimal("40000"),
            "q3": Decimal("45000"),
            "q4": Decimal("50000"),
            "total": Decimal("175000"),
            "status": "active",
            "spent": Decimal("2450"),
            "remaining": Decimal("37550"),
        },
        {
            "department": "Engineering",
            "q1": Decimal("60000"),
            "q2": Decimal("65000"),
            "q3": Decimal("65000"),
            "q4": Decimal("70000"),
            "total": Decimal("260000"),
            "status": "active",
            "spent": Decimal("0"),
            "remaining": Decimal("60000"),
        },
        {
            "department": "Sales",
            "q1": Decimal("30000"),
            "q2": Decimal("35000"),
            "q3": Decimal("40000"),
            "q4": Decimal("45000"),
            "total": Decimal("150000"),
            "status": "active",
            "spent": Decimal("0"),
            "remaining": Decimal("30000"),
        },
    ]


def generate_demo_forecasts(company_id: str) -> list[dict[str, Any]]:
    """Generate sample expense forecasts."""
    now = datetime.now()
    base_date = now.replace(day=1)

    return [
        {
            "month": (base_date + timedelta(days=30)).strftime("%B %Y"),
            "forecasted_expense": Decimal("12500"),
            "confidence": 0.85,
            "trend": "increasing",
        },
        {
            "month": (base_date + timedelta(days=60)).strftime("%B %Y"),
            "forecasted_expense": Decimal("14200"),
            "confidence": 0.72,
            "trend": "increasing",
        },
        {
            "month": (base_date + timedelta(days=90)).strftime("%B %Y"),
            "forecasted_expense": Decimal("13800"),
            "confidence": 0.65,
            "trend": "stable",
        },
    ]
