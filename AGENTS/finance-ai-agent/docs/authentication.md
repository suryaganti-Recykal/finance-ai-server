# Authentication

The platform uses **Clerk** for identity management and authentication. Clerk handles user sign-up, sign-in, MFA, and organization management on the frontend. The backend verifies Clerk JWTs and syncs user/organization data into the local database.

## Setup

### 1. Create Clerk project

- Sign up at https://dashboard.clerk.com
- Create a new application
- Copy credentials to `.env`:
  ```env
  CLERK_SECRET_KEY=sk_test_...
  CLERK_PUBLISHABLE_KEY=pk_test_...
  CLERK_JWKS_URL=https://<your-clerk-domain>/.well-known/jwks.json
  ```

### 2. Frontend setup (Next.js)

The frontend (`apps/web`) wraps the app with Clerk's provider and uses Clerk's UI components for sign-up/sign-in.

```tsx
import { ClerkProvider } from "@clerk/nextjs";
import { useAuth, useUser } from "@clerk/nextjs";

export default function RootLayout({ children }) {
  return (
    <ClerkProvider>
      <YourApp />
    </ClerkProvider>
  );
}

function YourComponent() {
  const { getToken } = useAuth();
  const { user } = useUser();

  // Send token to backend
  const response = await fetch("/api/v1/auth/me", {
    headers: {
      Authorization: `Bearer ${await getToken()}`,
    },
  });
}
```

### 3. Backend flow

```
Frontend (Next.js + Clerk UI)
  ↓
User signs up / logs in
  ↓
Clerk issues JWT (includes org_id, user_id, email, etc.)
  ↓
Frontend sends request with "Authorization: Bearer <jwt>"
  ↓
Backend API
  ├─ RequestContextMiddleware extracts request id
  ├─ get_current_company_id() dependency:
  │   ├─ Extracts Bearer token from Authorization header
  │   ├─ Calls ClerkAuthService.verify_token()
  │   ├─ JWKS verification (RSA + RS256)
  │   ├─ Extracts org_id claim
  │   └─ Sets contextvars (request_id, company_id, user_id)
  ├─ Router calls use case
  ├─ Use case queries database (company/user) — filtered by company_id
  └─ Response (tenant-isolated)
```

## JWT verification

Backend verifies JWTs without calling Clerk APIs (after initial JWKS fetch):

- **JWKS URL**: configured in `CLERK_JWKS_URL`
- **Algorithm**: RS256 (RSA)
- **Audience**: your `CLERK_PUBLISHABLE_KEY`
- **Claims used**:
  - `org_id` → company_id (filter all queries by tenant)
  - `sub` (subject) → user_id (Clerk's internal user ID)
  - `email` → user's email
  - `given_name`, `family_name` → first/last name

## Organization setup (Clerk dashboard)

1. Enable **Organizations** in your Clerk project settings
2. Users create or join organizations (companies)
3. Each JWT includes the selected `org_id`
4. Platform stores company data locally (name, logo, etc.) when first accessed

## API endpoints

### GET /auth/me
Get the currently authenticated user's profile.

**Request:**
```bash
curl -H "Authorization: Bearer <jwt>" \
  http://localhost:8000/api/v1/auth/me
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "user_123",
    "company_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "admin",
    "is_active": true,
    "created_at": "2026-07-01T10:00:00Z"
  }
}
```

**Errors:**
- `401 unauthorized`: Missing or invalid Authorization header
- `401 unauthorized`: Token signature invalid or expired
- `401 unauthorized`: No org_id in token (user hasn't selected an organization)

## Multi-tenancy enforcement

Every API endpoint is tenant-scoped:

1. `CurrentCompanyId` dependency resolves company_id from JWT
2. All repositories filter by `company_id` (enforced at the base `SQLAlchemyRepository`)
3. One user can never read another tenant's data

Example:
```python
async def get_expense(
    company_id: CurrentCompanyId,  # ← Clerk org_id
    expense_id: uuid.UUID,
    db: DbSession,
) -> SuccessResponse[ExpenseOutput]:
    # ExpenseRepository.get_by_id() enforces:
    # WHERE id = expense_id AND company_id = company_id
    # So user cannot access expenses from other orgs
```

## Development / Testing

### Mock JWT in tests

```python
from unittest.mock import AsyncMock, patch

with patch("src.api.deps.get_clerk_auth") as mock_clerk:
    mock_service = AsyncMock()
    mock_service.extract_company_id = AsyncMock(return_value=company_id)
    mock_service.extract_user_id = AsyncMock(return_value=user_id)
    mock_clerk.return_value = mock_service
    
    # Now requests with any Authorization header will use mocked values
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer fake_token"},
    )
```

### Bypass auth in development

To test without Clerk, comment out the `CurrentCompanyId` dependency and hardcode:
```python
from src.core.security.context import set_current_company_id

async def startup():
    dev_company_id = uuid.UUID("00000000-0000-0000-0000-000000000000")
    set_current_company_id(dev_company_id)
```

## Security notes

- **JWKS caching**: `ClerkAuthService._jwks_cache` stores fetched keys to avoid repeated HTTP calls. Keys rotate rarely; a 1-hour expiry TTL can be added if needed.
- **No user creation on JWT validation**: The backend queries the database for user record (sync may have failed). If not found, returns 404 (user must be created via sign-up flow first).
- **Tokens in logs**: Request/response bodies are not logged (use `LOG_LEVEL=DEBUG` only in development). Never log Authorization headers.
- **HTTPS in production**: JWTs must be transmitted over HTTPS in production.

## References

- [Clerk docs](https://clerk.com/docs)
- [JWT.io (inspector)](https://jwt.io)
- [Clerk JWKS endpoint](https://clerk.com/docs/backend-requests/handling/jwt-verification#validate-tokens-with-jwks)
