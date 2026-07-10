import uuid

from sqlalchemy import select

from src.domain.users.entities.user import User
from src.domain.users.repositories.user import UserRepository
from src.infrastructure.db.models.user import UserModel
from src.infrastructure.db.repository import SQLAlchemyRepository


class UserRepositoryImpl(SQLAlchemyRepository[UserModel, User], UserRepository):
    """SQLAlchemy-based implementation of UserRepository."""

    model = UserModel

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            company_id=model.company_id,
            email=model.email,
            first_name=model.first_name,
            last_name=model.last_name,
            role=model.role,
            is_active=model.is_active,
            created_at=model.created_at,
        )

    def _to_model(self, entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            company_id=entity.company_id,
            email=entity.email,
            first_name=entity.first_name,
            last_name=entity.last_name,
            role=entity.role,
            is_active=entity.is_active,
            created_at=entity.created_at,
        )

    async def get_by_email(self, company_id: uuid.UUID, email: str) -> User | None:
        stmt = select(self.model).where(
            self.model.company_id == company_id, self.model.email == email
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row is not None else None

    async def get_by_company(self, company_id: uuid.UUID) -> list[User]:
        stmt = select(self.model).where(self.model.company_id == company_id)
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return [self._to_entity(r) for r in rows]
