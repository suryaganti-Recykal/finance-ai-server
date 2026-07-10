"""Demo mode endpoints for presentations.

Provides sample data and quick-start functionality for showcasing agents.
"""

from typing import Any

from fastapi import APIRouter, Header

from src.infrastructure.demo_data import (
    generate_demo_budgets,
    generate_demo_expenses,
    generate_demo_forecasts,
    generate_demo_marketing_campaigns,
)
from src.schemas.common import SuccessResponse

router = APIRouter(prefix="/demo", tags=["demo"])


@router.get("/expenses", response_model=SuccessResponse[list[dict[str, Any]]])
async def get_demo_expenses(x_company_id: str = Header(default="demo-company-001")) -> SuccessResponse[list[dict[str, Any]]]:
    """Get sample expense data for demo/presentation."""
    transactions = generate_demo_expenses(x_company_id)
    data = [
        {
            "id": tx.source_transaction_id,
            "source": tx.source,
            "description": tx.description,
            "amount": float(tx.amount),
            "currency": tx.currency,
            "category": tx.category,
            "date": tx.transaction_date.isoformat(),
            "merchant": tx.merchant,
        }
        for tx in transactions
    ]
    return SuccessResponse(data=data, message="Demo expenses loaded")


@router.get("/marketing", response_model=SuccessResponse[list[dict[str, Any]]])
async def get_demo_marketing(x_company_id: str = Header(default="demo-company-001")) -> SuccessResponse[list[dict[str, Any]]]:
    """Get sample marketing campaign data for demo."""
    campaigns = generate_demo_marketing_campaigns(x_company_id)
    return SuccessResponse(data=campaigns, message="Demo marketing campaigns loaded")


@router.get("/budgets", response_model=SuccessResponse[list[dict[str, Any]]])
async def get_demo_budgets(x_company_id: str = Header(default="demo-company-001")) -> SuccessResponse[list[dict[str, Any]]]:
    """Get sample budget allocation data for demo."""
    budgets = generate_demo_budgets(x_company_id)
    return SuccessResponse(data=budgets, message="Demo budgets loaded")


@router.get("/forecasts", response_model=SuccessResponse[list[dict[str, Any]]])
async def get_demo_forecasts(x_company_id: str = Header(default="demo-company-001")) -> SuccessResponse[list[dict[str, Any]]]:
    """Get sample forecast data for demo."""
    forecasts = generate_demo_forecasts(x_company_id)
    return SuccessResponse(data=forecasts, message="Demo forecasts loaded")


@router.get("/all", response_model=SuccessResponse[dict[str, Any]])
async def get_all_demo_data(x_company_id: str = Header(default="demo-company-001")) -> SuccessResponse[dict[str, Any]]:
    """Get all demo data at once."""
    expenses_raw = generate_demo_expenses(x_company_id)
    expenses = [
        {
            "id": tx.source_transaction_id,
            "source": tx.source,
            "description": tx.description,
            "amount": float(tx.amount),
            "category": tx.category,
            "date": tx.transaction_date.isoformat(),
            "merchant": tx.merchant,
        }
        for tx in expenses_raw
    ]

    return SuccessResponse(
        data={
            "expenses": expenses,
            "marketing": generate_demo_marketing_campaigns(x_company_id),
            "budgets": generate_demo_budgets(x_company_id),
            "forecasts": generate_demo_forecasts(x_company_id),
        },
        message="All demo data loaded",
    )
