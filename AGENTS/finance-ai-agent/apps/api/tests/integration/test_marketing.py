import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, patch

from httpx import AsyncClient

from src.infrastructure.db.models.campaign import CampaignModel
from src.infrastructure.db.models.company import CompanyModel
from src.infrastructure.db.session import AsyncSessionLocal


async def test_get_marketing_report(client: AsyncClient) -> None:
    """Test GET /marketing returns campaign KPIs and anomalies."""
    company_id = uuid.uuid4()
    user_id = "user_clerk_123"

    with patch("src.api.deps.get_clerk_auth") as mock_clerk:
        mock_service = AsyncMock()
        mock_service.extract_company_id = AsyncMock(return_value=company_id)
        mock_service.extract_user_id = AsyncMock(return_value=user_id)
        mock_clerk.return_value = mock_service

        # Create company and campaign
        async with AsyncSessionLocal() as session:
            company = CompanyModel(
                id=company_id, name="Test Co", email="test@example.com", slug="test-co"
            )
            session.add(company)
            await session.flush()

            now = datetime.now(timezone.utc)
            campaign = CampaignModel(
                id=uuid.uuid4(),
                company_id=company_id,
                name="Summer Sale",
                platform="meta",
                campaign_id="meta_123456",
                total_spend=Decimal("5000"),
                currency="USD",
                leads=150,
                purchases=25,
                impressions=50000,
                clicks=1000,
                status="active",
                start_date=now,
                end_date=None,
            )
            session.add(campaign)
            await session.commit()

        # Get report
        response = await client.get(
            "/api/v1/marketing",
            headers={"Authorization": "Bearer fake_jwt_token"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert "data" in body
        data = body["data"]

        # Check overall metrics
        assert data["total_spend"] == "5000"
        assert data["total_leads"] == 150
        assert data["total_purchases"] == 25
        assert data["total_impressions"] == 50000
        assert data["total_clicks"] == 1000

        # Check campaign-level KPIs
        assert len(data["campaigns"]) == 1
        campaign_data = data["campaigns"][0]
        assert campaign_data["campaign_name"] == "Summer Sale"
        assert campaign_data["platform"] == "meta"
        assert campaign_data["cpl"] == "33.33"  # 5000 / 150


async def test_marketing_report_missing_auth(client: AsyncClient) -> None:
    """Test GET /marketing without Authorization header."""
    response = await client.get("/api/v1/marketing")
    assert response.status_code == 401
