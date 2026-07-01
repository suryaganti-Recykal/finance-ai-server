import uuid
from abc import abstractmethod

from src.domain.companies.entities.company import Company
from src.domain.shared.repositories.base import AbstractRepository


class CompanyRepository(AbstractRepository[Company]):
    """Repository for company entities."""

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Company | None:
        """Get company by slug (for initialization/lookup)."""
        ...
