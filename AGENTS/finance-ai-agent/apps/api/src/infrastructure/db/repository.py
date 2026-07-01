import uuid
from typing import Generic, TypeVar

from sqlalchemy import delete as sa_delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.shared.entities.base import TenantScopedEntity
from src.domain.shared.repositories.base import AbstractRepository
from src.infrastructure.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)
EntityT = TypeVar("EntityT", bound=TenantScopedEntity)


class SQLAlchemyRepository(AbstractRepository[EntityT], Generic[ModelT, EntityT]):
    """Reusable, company-scoped CRUD implementation over a SQLAlchemy model.

    Concrete repositories (e.g. ExpenseRepository, defined alongside the
    expenses module once its ORM model exists) subclass this with their
    model/entity pair and implement `_to_entity` / `_to_model` to translate
    between the ORM row and the domain dataclass.
    """

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: ModelT) -> EntityT:
        raise NotImplementedError

    def _to_model(self, entity: EntityT) -> ModelT:
        raise NotImplementedError

    async def get_by_id(self, company_id: uuid.UUID, entity_id: uuid.UUID) -> EntityT | None:
        stmt = select(self.model).where(
            self.model.id == entity_id, self.model.company_id == company_id
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row is not None else None

    async def list(
        self, company_id: uuid.UUID, *, offset: int = 0, limit: int = 20
    ) -> list[EntityT]:
        stmt = (
            select(self.model)
            .where(self.model.company_id == company_id)
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(row) for row in result.scalars().all()]

    async def add(self, entity: EntityT) -> EntityT:
        model = self._to_model(entity)
        self._session.add(model)
        await self._session.flush()
        return self._to_entity(model)

    async def update(self, entity: EntityT) -> EntityT:
        model = await self._session.merge(self._to_model(entity))
        await self._session.flush()
        return self._to_entity(model)

    async def delete(self, company_id: uuid.UUID, entity_id: uuid.UUID) -> None:
        stmt = sa_delete(self.model).where(
            self.model.id == entity_id, self.model.company_id == company_id
        )
        await self._session.execute(stmt)
