import uuid
from dataclasses import dataclass
from datetime import datetime

from src.application.shared.use_case import UseCase
from src.core.exceptions.base import NotFoundException
from src.domain.users.repositories.user import UserRepository


@dataclass(kw_only=True)
class GetCurrentUserInput:
    company_id: uuid.UUID
    user_id: str


@dataclass(kw_only=True)
class GetCurrentUserOutput:
    id: str
    company_id: uuid.UUID
    email: str
    first_name: str | None
    last_name: str | None
    role: str
    is_active: bool
    created_at: datetime | None


class GetCurrentUserUseCase(UseCase[GetCurrentUserInput, GetCurrentUserOutput]):
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    async def execute(self, input_data: GetCurrentUserInput) -> GetCurrentUserOutput:
        user = await self.user_repo.get_by_id(input_data.company_id, input_data.user_id)
        if not user:
            raise NotFoundException(f"User {input_data.user_id} not found in company.")

        return GetCurrentUserOutput(
            id=user.id,
            company_id=user.company_id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
        )
