import uuid
from dataclasses import dataclass

from src.application.shared.use_case import UseCase
from src.core.exceptions.base import NotFoundException
from src.domain.companies.repositories.company import CompanyRepository


@dataclass(kw_only=True)
class GetCompanyInput:
    company_id: uuid.UUID


@dataclass(kw_only=True)
class GetCompanyOutput:
    id: uuid.UUID
    name: str
    email: str
    slug: str
    logo_url: str | None
    website: str | None
    is_active: bool


class GetCompanyUseCase(UseCase[GetCompanyInput, GetCompanyOutput]):
    def __init__(self, company_repo: CompanyRepository) -> None:
        self.company_repo = company_repo

    async def execute(self, input_data: GetCompanyInput) -> GetCompanyOutput:
        company = await self.company_repo.get_by_id(input_data.company_id, input_data.company_id)
        if not company:
            raise NotFoundException(f"Company {input_data.company_id} not found.")

        return GetCompanyOutput(
            id=company.id,
            name=company.name,
            email=company.email,
            slug=company.slug,
            logo_url=company.logo_url,
            website=company.website,
            is_active=company.is_active,
        )
