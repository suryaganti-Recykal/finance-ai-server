import uuid
from abc import abstractmethod

from src.domain.shared.repositories.base import AbstractRepository
from src.domain.users.entities.user import User


class UserRepository(AbstractRepository[User]):
    """Repository for user entities."""

    @abstractmethod
    async def get_by_email(self, company_id: uuid.UUID, email: str) -> User | None:
        """Get user by email within a company."""
        ...
