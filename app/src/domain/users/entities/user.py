import uuid
from dataclasses import dataclass
from datetime import datetime

from src.domain.shared.entities.base import TenantScopedEntity


@dataclass(kw_only=True)
class User(TenantScopedEntity):
    """A user within a company."""

    id: str  # Clerk user_id
    email: str
    first_name: str | None = None
    last_name: str | None = None
    role: str = "member"
    is_active: bool = True
    created_at: datetime | None = None
