# Database Migrations (Alembic)

## Structure

```
apps/api/
├── alembic.ini                          # Alembic config
├── alembic/
│   ├── env.py                           # Migration runner (reads DATABASE_URL, auto-detects models)
│   ├── script.py.mako                   # Migration script template
│   └── versions/
│       └── 001_initial_schema.py        # Schema creation
```

## Running migrations

### Apply pending migrations (on boot or manual)
```bash
cd apps/api
alembic upgrade head
```

### Revert to previous revision
```bash
alembic downgrade -1
```

### View current migration state
```bash
alembic current
```

## Adding new models or columns

Once you add a model to `src/infrastructure/db/models/`:

1. Import it in `src/infrastructure/db/models/__init__.py`
2. Generate migration (requires Python 3.12 + `pip install -e .[dev]`):
   ```bash
   alembic revision --autogenerate -m "Add <feature>"
   ```
3. Review the generated `alembic/versions/XXX_add_<feature>.py`
4. Apply:
   ```bash
   alembic upgrade head
   ```

**Why `env.py` imports `src.infrastructure.db.models`**: so Alembic's autogenerate can discover all models
and detect schema diffs. Without the import, new tables won't appear in generated migrations.

## Docker Compose

The `docker-compose.yml` includes a Postgres service. Migrations run automatically on container boot via entrypoint.

## Notes

- This project uses **async SQLAlchemy** (asyncpg dialect). The Alembic env.py wraps async operations.
- The declarative base (`src.infrastructure.db.base.Base`) includes a **naming convention** so constraint names are predictable across all environments.
- All tables are **tenant-scoped** (company_id foreign key) — multi-tenant at the row level.
- Timestamps (created_at, updated_at) are in **UTC with timezone awareness**.
