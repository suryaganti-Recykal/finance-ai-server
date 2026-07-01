from typing import Any


class AppException(Exception):
    """Base class for all domain/application exceptions.

    Raised by domain and application layers; translated to HTTP responses
    by the handlers registered in core/exceptions/handlers.py. Layers below
    the API never import FastAPI or know about status codes directly - they
    only need to raise the right AppException subclass.
    """

    status_code: int = 500
    code: str = "internal_error"

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(message)


class NotFoundException(AppException):
    status_code = 404
    code = "not_found"


class ValidationException(AppException):
    status_code = 422
    code = "validation_error"


class UnauthorizedException(AppException):
    status_code = 401
    code = "unauthorized"


class ForbiddenException(AppException):
    status_code = 403
    code = "forbidden"


class ConflictException(AppException):
    status_code = 409
    code = "conflict"


class ExternalServiceException(AppException):
    """Raised when a downstream integration (Zoho, Meta, Google Ads, Razorpay, LLM providers) fails."""

    status_code = 502
    code = "external_service_error"
