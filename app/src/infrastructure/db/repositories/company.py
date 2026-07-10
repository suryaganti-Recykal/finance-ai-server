
from sqlalchemy import select

from src.domain.companies.entities.company import Company
from src.domain.companies.repositories.company import CompanyRepository
from src.infrastructure.db.models.company import CompanyModel
from src.infrastructure.db.repository import SQLAlchemyRepository


class CompanyRepositoryImpl(SQLAlchemyRepository[CompanyModel, Company], CompanyRepository):
    """SQLAlchemy-based implementation of CompanyRepository."""

    model = CompanyModel

    def _to_entity(self, model: CompanyModel) -> Company:
        return Company(
            id=model.id,
            name=model.name,
            email=model.email,
            slug=model.slug,
            logo_url=model.logo_url,
            website=model.website,
            is_active=model.is_active,
        )

    def _to_model(self, entity: Company) -> CompanyModel:
        return CompanyModel(
            id=entity.id,
            name=entity.name,
            email=entity.email,
            slug=entity.slug,
            logo_url=entity.logo_url,
            website=entity.website,
            is_active=entity.is_active,
        )

    async def get_by_slug(self, slug: str) -> Company | None:
        stmt = select(self.model).where(self.model.slug == slug)
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row is not None else None
