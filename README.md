# Finance AI Agent - Isolated Development Server

This is a **clean, isolated server environment** for the Finance AI Agent SaaS platform. All dependencies are contained in a local virtual environment to avoid conflicts with your system Python.

## 📁 Directory Structure

```
finance-ai-server/
├── venv/                 # Python virtual environment (isolated)
├── app/                  # FastAPI application code
│   ├── src/             # Source code (domain, application, infrastructure, API)
│   ├── alembic/         # Database migrations
│   ├── pyproject.toml   # Python dependencies
│   ├── .env             # Environment variables (local)
│   └── .env.example     # Environment template
├── logs/                # Application logs
├── data/                # Local database (if using SQLite)
├── start-server.bat     # Windows batch startup script
├── start-server.ps1     # PowerShell startup script
└── README.md            # This file
```

## 🚀 Quick Start

### Option 1: PowerShell (Recommended)

```powershell
cd C:\Users\surya.ganti\finance-ai-server
.\start-server.ps1
```

### Option 2: Command Prompt (Batch)

```cmd
cd C:\Users\surya.ganti\finance-ai-server
start-server.bat
```

### Option 3: Manual

```powershell
cd C:\Users\surya.ganti\finance-ai-server\app

# Activate virtual environment
..\venv\Scripts\Activate.ps1

# Run server
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

## ✅ Verification

Once the server starts, you should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Test Health Endpoints

```bash
# Basic health
curl http://127.0.0.1:8000/api/v1/health

# Database health
curl http://127.0.0.1:8000/api/v1/health/db
```

### Interactive API Documentation

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## 🔧 Environment Configuration

The `.env` file contains all configuration:

```env
ENVIRONMENT=development
DEBUG=true
API_PORT=8000
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/finance_ai_dev
```

### Setting Real Credentials

1. Open `app/.env`
2. Replace placeholder values:
   - `CLERK_SECRET_KEY`: Get from Clerk dashboard
   - `CLERK_PUBLISHABLE_KEY`: Get from Clerk dashboard
   - `OPENAI_API_KEY`: Get from OpenAI console
   - `ANTHROPIC_API_KEY`: Get from Anthropic console
   - `DATABASE_URL`: Point to your PostgreSQL instance

## 🗄️ Database Setup

### Initialize Database (First Time)

```powershell
cd app

# Run migrations
python -m alembic upgrade head

# Or drop and recreate
python -m alembic downgrade base
python -m alembic upgrade head
```

### Using PostgreSQL

```powershell
# Install PostgreSQL (if needed)
# https://www.postgresql.org/download/windows/

# Create database
psql -U postgres -c "CREATE DATABASE finance_ai_dev;"

# Update .env with your connection
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/finance_ai_dev
```

### Using SQLite (Development Only)

For quick testing without PostgreSQL:

```env
DATABASE_URL=sqlite+aiosqlite:///./finance_ai_dev.db
```

## 📊 API Endpoints

### Available Routes

| Category | Endpoint | Method | Status |
|----------|----------|--------|--------|
| Health | `/api/v1/health` | GET | ✅ |
| Health | `/api/v1/health/db` | GET | ✅ |
| Auth | `/api/v1/auth/me` | GET | ✅ |
| Dashboard | `/api/v1/dashboard` | GET | ✅ |
| Dashboard | `/api/v1/dashboard/trends` | GET | ✅ |
| Dashboard | `/api/v1/dashboard/department-spend` | GET | ✅ |
| Dashboard | `/api/v1/dashboard/budget-utilization` | GET | ✅ |
| Dashboard | `/api/v1/dashboard/campaigns` | GET | ✅ |
| Expenses | `/api/v1/expenses/sync` | POST | ✅ |
| Marketing | `/api/v1/marketing` | GET | ✅ |
| Budgets | `/api/v1/budgets` | GET | ✅ |

## 🧪 Testing

### Run Tests

```powershell
cd app

# Activate venv
..\venv\Scripts\Activate.ps1

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/integration/test_dashboard.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'src'"

**Solution:** Ensure the virtual environment is activated:

```powershell
..\venv\Scripts\Activate.ps1
```

### Issue: "Database connection refused"

**Solution:** Check PostgreSQL is running and credentials in `.env` are correct:

```powershell
# Test connection
python -c "from src.infrastructure.db.session import engine; engine"
```

### Issue: "Port 8000 already in use"

**Solution:** Change port in startup script or kill existing process:

```powershell
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use different port
python -m uvicorn src.main:app --port 8001 --reload
```

### Issue: Missing dependencies

**Solution:** Reinstall from pyproject.toml:

```powershell
cd app
python -m pip install -e .
```

## 📚 Project Structure

```
app/src/
├── main.py                    # FastAPI factory
├── api/                       # HTTP layer
│   ├── v1/
│   │   ├── router.py         # API router aggregator
│   │   └── routers/          # Feature routers
│   └── deps.py               # Dependency injection
├── application/              # Use case layer
│   ├── shared/              # Base use cases
│   └── <module>/            # Feature use cases
├── domain/                   # Business logic layer
│   ├── shared/              # Shared entities
│   └── <module>/            # Feature entities
├── infrastructure/           # External systems layer
│   ├── db/
│   │   ├── models/          # SQLAlchemy ORM
│   │   ├── repositories/    # Database queries
│   │   └── base.py          # Session factory
│   └── connectors/          # External integrations
├── core/                     # Cross-cutting concerns
│   ├── config/              # Settings
│   ├── security/            # Auth & context
│   ├── exceptions/          # Error handling
│   └── logging/             # Structured logging
└── schemas/                  # Pydantic DTOs
```

## 🚀 Development Workflow

1. **Start the server**: `.\start-server.ps1`
2. **Open Swagger UI**: http://127.0.0.1:8000/docs
3. **Edit code** in `app/src/`
4. **Hot reload** automatically picks up changes (--reload flag)
5. **Test in Swagger** or with curl/Postman
6. **Run tests**: `pytest tests/ -v`

## 📝 Key Files

- **Configuration**: `app/src/core/config/settings.py`
- **Database**: `app/src/infrastructure/db/`
- **API Routes**: `app/src/api/v1/routers/`
- **Business Logic**: `app/src/application/`
- **Domain Entities**: `app/src/domain/`
- **Migrations**: `app/alembic/versions/`

## 🔗 External Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy 2.0**: https://docs.sqlalchemy.org/
- **Alembic**: https://alembic.sqlalchemy.org/
- **Pydantic**: https://docs.pydantic.dev/
- **Clerk**: https://clerk.com/docs

## 📞 Support

For issues or questions:

1. Check logs in `logs/` directory
2. Review `.env` configuration
3. Verify database connection
4. Run tests to isolate issues
5. Check API documentation at `/docs`

---

**Status**: ✅ Server ready for development

**Last Updated**: 2026-07-01
