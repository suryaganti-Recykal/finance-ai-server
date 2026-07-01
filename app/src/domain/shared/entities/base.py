import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(kw_only=True)
class Entity:
    """Base for every domain entity - identity independent of persistence."""

    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(kw_only=True)
class TenantScopedEntity(Entity):
    """Base for entities that belong to a single company.

    Every business entity in this platform (expenses, revenue, budgets, ...)
    is tenant-scoped so the same schema can serve multiple companies. Row-level
    scoping (company_id column) was chosen over schema-per-tenant or
    database-per-tenant for operational simplicity at this stage; repositories
    are responsible for always filtering by company_id.
    """

    company_id: uuid.UUID


@dataclass(kw_only=True)
class AggregateRoot(TenantScopedEntity):
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
