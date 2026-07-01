import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.core.security.context import set_request_id


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Assigns a request id used to correlate logs across a single request.

    Tenant/user context is bound later, by the auth dependency in api/deps.py,
    once the request has been authenticated - this middleware only handles
    what's available before auth runs.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        set_request_id(request_id)

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
