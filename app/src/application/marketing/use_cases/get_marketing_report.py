import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from src.application.marketing.services.calculation_service import MarketingMetricsService
from src.application.shared.use_case import UseCase
from src.domain.marketing.entities.metrics import MarketingReport
from src.domain.marketing.repositories.marketing import MarketingRepository


@dataclass(kw_only=True)
class GetMarketingReportInput:
    company_id: uuid.UUID
    start_date: datetime | None = None
    end_date: datetime | None = None


class GetMarketingReportUseCase(UseCase[GetMarketingReportInput, MarketingReport]):
    """Generate a marketing report with all campaigns, KPIs, and anomalies."""

    def __init__(self, marketing_repo: MarketingRepository) -> None:
        self.marketing_repo = marketing_repo

    async def execute(self, input_data: GetMarketingReportInput) -> MarketingReport:
        now = datetime.now(UTC)
        end_date = input_data.end_date or now
        start_date = input_data.start_date or (now - timedelta(days=30))

        service = MarketingMetricsService(self.marketing_repo)
        report = await service.generate_report(input_data.company_id, start_date, end_date)

        return report
