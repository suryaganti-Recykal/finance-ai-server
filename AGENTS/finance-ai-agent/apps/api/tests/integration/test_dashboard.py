import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, patch

from httpx import AsyncClient

from src.infrastructure.db.models.company import CompanyModel
from src.infrastructure.db.models.expense import ExpenseModel
from src.infrastructure.db.models.revenue import RevenueModel
from src.infrastructure.db.session import AsyncSessionLocal


async def test_get_dashboard_kpis(client: AsyncClient) -> None:
    """Test GET /dashboard returns KPIs for the period."""
    company_id = uuid.uuid4()
    user_id = "user_clerk_123"

    with patch("src.api.deps.get_clerk_auth") as mock_clerk:
        mock_service = AsyncMock()
        mock_service.extract_company_id = AsyncMock(return_value=company_id)
        mock_service.extract_user_id = AsyncMock(return_value=user_id)
        mock_clerk.return_value = mock_service

        # Create test data
        async with AsyncSessionLocal() as session:
            company = CompanyModel(
                id=company_id, name="Test Co", email="test@example.com", slug="test-co"
            )
            session.add(company)
            await session.flush()

            now = datetime.now(timezone.utc)
            revenue = RevenueModel(
                id=uuid.uuid4(),
                company_id=company_id,
                amount=Decimal("10000"),
                currency="USD",
                source="stripe",
                revenue_date=now,
            )
            expense = ExpenseModel(
                id=uuid.uuid4(),
                company_id=company_id,
                amount=Decimal("3000"),
                currency="USD",
                category="marketing",
                source="meta",
                expense_date=now,
            )
            session.add(revenue)
            session.add(expense)
            await session.commit()

        # Make request
        response = await client.get(
            "/api/v1/dashboard",
            headers={"Authorization": "Bearer fake_jwt_token"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert "data" in body
        assert "kpis" in body["data"]
        kpis = body["data"]["kpis"]

        # Check KPI values
        assert kpis["revenue"]["value"] == "10000"
        assert kpis["expenses"]["value"] == "3000"
        assert kpis["profit"]["value"] == "7000"


async def test_get_dashboard_missing_auth(client: AsyncClient) -> None:
    """Test GET /dashboard without Authorization header."""
    response = await client.get("/api/v1/dashboard")
    assert response.status_code == 401


async def test_get_department_spend(client: AsyncClient) -> None:
    """Test GET /dashboard/department-spend returns breakdown."""
    company_id = uuid.uuid4()
    user_id = "user_clerk_123"

    with patch("src.api.deps.get_clerk_auth") as mock_clerk:
        mock_service = AsyncMock()
        mock_service.extract_company_id = AsyncMock(return_value=company_id)
        mock_service.extract_user_id = AsyncMock(return_value=user_id)
        mock_clerk.return_value = mock_service

        async with AsyncSessionLocal() as session:
            company = CompanyModel(
                id=company_id, name="Test Co", email="test@example.com", slug="test-co"
            )
            session.add(company)
            await session.commit()

        response = await client.get(
            "/api/v1/dashboard/department-spend",
            headers={"Authorization": "Bearer fake_jwt_token"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert "data" in body
