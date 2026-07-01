# Finance AI Agent

Cloud-based, multi-tenant AI Finance Assistant. Connects to financial systems,
imports and categorizes expenses, analyses marketing spend, maintains an
executive dashboard, generates reports, and proactively emails stakeholders -
functioning as an autonomous finance employee.

## Repository layout

```
apps/
  api/    FastAPI backend - Clean Architecture (domain / application / infrastructure / api), LangGraph agents
  web/    Next.js frontend - App Router, feature-based modules
packages/
  shared-types/   Types shared between frontend and backend
automation/
  n8n/            Scheduled/triggered workflow definitions (daily sync, monthly reports, budget alerts)
infra/            Docker, Railway, AWS deployment config
docs/             Architecture, API, agent, and database documentation
```

## Backend architecture (`apps/api`)

Clean Architecture with four layers, each module (expenses, revenue,
collections, marketing_spend, budgets, forecasting, reports, ...) repeated
consistently across layers:

- `src/domain/<module>` - entities, value objects, repository interfaces. No framework imports.
- `src/application/<module>` - use cases (one class per business action) and services, orchestrating domain + repositories.
- `src/infrastructure` - SQLAlchemy models/repositories, external connectors (`connectors/zoho`, `meta`, `google_ads`, `razorpay`, `bank_csv`), LLM clients (OpenAI, Claude), email, storage.
- `src/api/v1` - FastAPI routers, one per module, thin adapters over use cases.
- `src/agents` - LangGraph agent graphs, one directory per finance agent, sharing `agents/orchestration` and `agents/shared`.
- `src/core` - config, logging, exceptions, security context - cross-cutting, no business logic.

**Multi-tenancy**: every business entity is company-scoped (row-level, via a
`company_id` column/field), enforced in the generic repository base
(`src/infrastructure/db/repository.py`) so tenant isolation doesn't depend on
each use case remembering to filter correctly.

**Status of auth**: `src/api/deps.py` resolves the current company/user from
`X-Company-Id` / `X-User-Id` headers as a placeholder. The Authentication step
replaces the body of `get_current_company_id` with Clerk JWT verification -
the dependency's signature (and therefore every router using it) stays the same.

## Local development

```bash
cp apps/api/.env.example apps/api/.env
docker compose up --build
# API: http://localhost:8000/docs
```

Backend tests:

```bash
cd apps/api
pip install -e ".[dev]"
pytest
```

## Build plan (incremental)

1. ✅ Folder structure
2. ✅ Backend architecture (this step)
3. Database schema + migrations
4. Authentication (Clerk)
5. Dashboard module
6. Expense Collection Agent
7. ... remaining modules and agents, one at a time
