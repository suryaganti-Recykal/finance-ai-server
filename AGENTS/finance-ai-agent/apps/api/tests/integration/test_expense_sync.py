import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, patch

from httpx import AsyncClient

from src.infrastructure.db.models.company import CompanyModel
from src.infrastructure.db.session import AsyncSessionLocal


async def test_sync_expenses_endpoint(client: AsyncClient) -> None:
    """Test POST /expenses/sync syncs and stores expenses."""
    company_id = uuid.uuid4()
    user_id = "user_clerk_123"

    with patch("src.api.deps.get_clerk_auth") as mock_clerk:
        mock_service = AsyncMock()
        mock_service.extract_company_id = AsyncMock(return_value=company_id)
        mock_service.extract_user_id = AsyncMock(return_value=user_id)
        mock_clerk.return_value = mock_service

        # Create company
        async with AsyncSessionLocal() as session:
            company = CompanyModel(
                id=company_id, name="Test Co", email="test@example.com", slug="test-co"
            )
            session.add(company)
            await session.commit()

        # Call sync endpoint
        response = await client.post(
            "/api/v1/expenses/sync",
            headers={"Authorization": "Bearer fake_jwt_token"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert "data" in body
        data = body["data"]
        assert "total_synced" in data
        assert "total_duplicates" in data
        assert "errors" in data


async def test_sync_expenses_missing_auth(client: AsyncClient) -> None:
    """Test POST /expenses/sync without Authorization header."""
    response = await client.post("/api/v1/expenses/sync")
    assert response.status_code == 401
