import uuid

from fastapi import APIRouter

from src.api.deps import CurrentCompanyId, CurrentUserId, DbSession
from src.application.users.use_cases.get_current_user import (
    GetCurrentUserInput,
    GetCurrentUserOutput,
    GetCurrentUserUseCase,
)
from src.infrastructure.db.repositories.user import UserRepositoryImpl
from src.schemas.common import SuccessResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/me", response_model=SuccessResponse[GetCurrentUserOutput])
async def get_current_user(
    company_id: CurrentCompanyId,
    user_id: CurrentUserId,
    db: DbSession,
) -> SuccessResponse[GetCurrentUserOutput]:
    """Get the currently authenticated user's profile."""
    repo = UserRepositoryImpl(db)
    use_case = GetCurrentUserUseCase(repo)
    result = await use_case.execute(
        GetCurrentUserInput(company_id=company_id, user_id=user_id)
    )
    return SuccessResponse(data=result)
