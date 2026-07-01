"""Clerk auth integration: verify JWTs, extract organization & user claims, sync user on first login."""

import json
import uuid
from typing import Any

import httpx
import jwt

from src.core.config.settings import get_settings
from src.core.exceptions.base import UnauthorizedException


class ClerkAuthService:
    """Verify Clerk JWTs, extract claims, resolve user/org."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._jwks_cache: dict[str, Any] | None = None

    async def get_jwks(self) -> dict[str, Any]:
        """Fetch JWKS from Clerk once, cache it."""
        if self._jwks_cache:
            return self._jwks_cache
        if not self.settings.CLERK_JWKS_URL:
            raise UnauthorizedException("Clerk JWKS URL not configured.")
        async with httpx.AsyncClient() as client:
            response = await client.get(self.settings.CLERK_JWKS_URL)
            response.raise_for_status()
            self._jwks_cache = response.json()
            return self._jwks_cache

    async def verify_token(self, token: str) -> dict[str, Any]:
        """Verify JWT signature using Clerk's JWKS.

        Returns the decoded token payload (includes org_id, user_id, org_role, etc.).
        Raises UnauthorizedException if invalid.
        """
        try:
            # Decode without verification first to get the kid (key ID)
            unverified = jwt.decode(token, options={"verify_signature": False})
        except jwt.DecodeError as exc:
            raise UnauthorizedException("Malformed JWT.") from exc

        jwks = await self.get_jwks()
        keys = {key["kid"]: key for key in jwks.get("keys", [])}

        # Get the key ID from the token header
        try:
            header = jwt.get_unverified_header(token)
            kid = header.get("kid")
        except jwt.DecodeError as exc:
            raise UnauthorizedException("Invalid JWT header.") from exc

        if not kid or kid not in keys:
            raise UnauthorizedException("Token signed with unknown key.")

        key_data = keys[kid]

        try:
            # Verify and decode
            payload = jwt.decode(
                token,
                key=jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key_data)),
                algorithms=["RS256"],
                audience=self.settings.CLERK_PUBLISHABLE_KEY,
            )
            return payload
        except jwt.InvalidSignatureError as exc:
            raise UnauthorizedException("Invalid token signature.") from exc
        except jwt.ExpiredSignatureError as exc:
            raise UnauthorizedException("Token expired.") from exc
        except jwt.InvalidTokenError as exc:
            raise UnauthorizedException(f"Token validation failed: {exc}") from exc

    async def extract_company_id(self, token: str) -> uuid.UUID:
        """Extract organization (company) ID from Clerk token."""
        payload = await self.verify_token(token)

        # Clerk includes org_id in the token when a user has selected an org
        org_id = payload.get("org_id")
        if not org_id:
            raise UnauthorizedException("No organization context in token.")

        try:
            return uuid.UUID(org_id)
        except ValueError as exc:
            raise UnauthorizedException(f"Invalid org_id format: {org_id}") from exc

    async def extract_user_id(self, token: str) -> str:
        """Extract Clerk user ID from token."""
        payload = await self.verify_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException("No user ID in token.")
        return user_id

    async def extract_claims(self, token: str) -> dict[str, Any]:
        """Extract full claims dict (org_id, user_id, email, org_role, etc.)."""
        return await self.verify_token(token)


def get_clerk_auth() -> ClerkAuthService:
    """Dependency for auth service."""
    return ClerkAuthService()
