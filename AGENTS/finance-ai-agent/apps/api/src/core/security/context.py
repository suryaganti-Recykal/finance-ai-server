"""Request-scoped context (tenant, user, request id) shared across layers via contextvars.

Populated by RequestContextMiddleware and the auth dependencies in api/deps.py.
Keeping this as a narrow, dependency-free module lets domain/application code
read "who is asking" without importing FastAPI or SQLAlchemy.
"""

import uuid
from contextvars import ContextVar

_request_id: ContextVar[str | None] = ContextVar("request_id", default=None)
_company_id: ContextVar[uuid.UUID | None] = ContextVar("company_id", default=None)
_user_id: ContextVar[str | None] = ContextVar("user_id", default=None)


def set_request_id(request_id: str) -> None:
    _request_id.set(request_id)


def get_request_id() -> str | None:
    return _request_id.get()


def set_current_company_id(company_id: uuid.UUID) -> None:
    _company_id.set(company_id)


def get_current_company_id() -> uuid.UUID | None:
    return _company_id.get()


def set_current_user_id(user_id: str) -> None:
    _user_id.set(user_id)


def get_current_user_id() -> str | None:
    return _user_id.get()
