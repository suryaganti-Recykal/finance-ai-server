import uuid
from dataclasses import dataclass

from src.domain.shared.entities.base import Entity


@dataclass(kw_only=True)
class Company(Entity):
    """A tenant/organization."""

    name: str
    email: str
    slug: str
    logo_url: str | None = None
    website: str | None = None
    is_active: bool = True
