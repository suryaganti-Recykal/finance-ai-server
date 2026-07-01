import uuid
from unittest.mock import AsyncMock, patch

from httpx import AsyncClient

from src.infrastructure.db.models.user import UserModel
from src.infrastructure.db.session import AsyncSessionLocal


async def test_get_current_user_authenticated(client: AsyncClient) -> None:
    """Test GET /auth/me with valid JWT."""
    # Mock Clerk JWT verification
    company_id = uuid.uuid4()
    user_id = "user_clerk_123"

    with patch("src.api.deps.get_clerk_auth") as mock_clerk:
        mock_service = AsyncMock()
        mock_service.extract_company_id = AsyncMock(return_value=company_id)
        mock_service.extract_user_id = AsyncMock(return_value=user_id)
        mock_clerk.return_value = mock_service

        # Create test data
        async with AsyncSessionLocal() as session:
            from src.infrastructure.db.models.company import CompanyModel
            from src.infrastructure.db.models.user import UserModel

            company = CompanyModel(
                id=company_id, name="Test Co", email="test@example.com", slug="test-co"
            )
            session.add(company)
            await session.flush()

            user = UserModel(
                id=user_id,
                company_id=company_id,
                email="john@example.com",
                first_name="John",
                last_name="Doe",
                role="admin",
            )
            session.add(user)
            await session.commit()

        # Make request
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer fake_jwt_token"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["id"] == user_id
        assert body["data"]["email"] == "john@example.com"
        assert body["data"]["first_name"] == "John"


async def test_get_current_user_missing_auth_header(client: AsyncClient) -> None:
    """Test GET /auth/me without Authorization header."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "unauthorized"


async def test_get_current_user_invalid_token_format(client: AsyncClient) -> None:
    """Test GET /auth/me with invalid token format."""
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "InvalidFormat"},
    )
    assert response.status_code == 401
    body = response.json()
    assert body["error"]["code"] == "unauthorized"
