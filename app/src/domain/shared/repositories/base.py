import uuid
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from src.domain.shared.entities.base import TenantScopedEntity

EntityT = TypeVar("EntityT", bound=TenantScopedEntity)


class AbstractRepository(ABC, Generic[EntityT]):
    """Port implemented by every infrastructure repository.

    Every method is implicitly company-scoped: implementations must filter by
    company_id so one tenant's use cases can never read or mutate another
    tenant's rows, regardless of what the application layer passes in.
    """

    @abstractmethod
    async def get_by_id(self, company_id: uuid.UUID, entity_id: uuid.UUID) -> EntityT | None: ...

    @abstractmethod
    async def list(
        self, company_id: uuid.UUID, *, offset: int = 0, limit: int = 20
    ) -> list[EntityT]: ...

    @abstractmethod
    async def add(self, entity: EntityT) -> EntityT: ...

    @abstractmethod
    async def update(self, entity: EntityT) -> EntityT: ...

    @abstractmethod
    async def delete(self, company_id: uuid.UUID, entity_id: uuid.UUID) -> None: ...
