# Finance AI Server - Complete Setup & Presentation Guide

Professional Finance AI backend with modern React dashboard for presentations.

## 🚀 What's Included

### Backend (FastAPI)
- ✅ 7 LangGraph AI agents (expense collection, budget monitoring, marketing spend, etc.)
- ✅ Demo mode with sample data (6 expenses, 4 campaigns, 4 budgets, 3 forecasts)
- ✅ Google Sheets integration (OAuth2-ready)
- ✅ Multi-tenant support with Clerk authentication
- ✅ SQLAlchemy 2.0 async database (SQLite dev / PostgreSQL prod)
- ✅ Clean Architecture (Hexagonal)
- ✅ Comprehensive API documentation (Swagger)

### Frontend (React + Next.js)
- ✅ Modern dashboard with real-time charts
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ KPI cards, budget visualization, expense tracking
- ✅ Multiple pages (dashboard, expenses, budgets, marketing)
- ✅ Tailwind CSS + Recharts for data visualization
- ✅ TypeScript for type safety

### DevOps
- ✅ Docker Compose setup (one command to run everything)
- ✅ Production-ready Dockerfiles with multi-stage builds
- ✅ Environment-specific configurations
- ✅ Health checks and auto-restart

## 📋 Prerequisites

- Python 3.12+
- Node.js 18+ (for frontend)
- Docker & Docker Compose (optional, for containerized setup)
- Git

## ⚡ Quick Start (3 Minutes)

### Option 1: Docker (Easiest)

```bash
# Clone/navigate to project
cd finance-ai-server

# Start everything
docker-compose up --build

# Done! Access:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

#### Step 1: Start Backend

```bash
cd app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Run server
uvicorn src.main:app --reload

# Backend runs at: http://localhost:8000
```

#### Step 2: Start Frontend (New Terminal)

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Start dev server
npm run dev

# Frontend runs at: http://localhost:3000
```

## 📊 Demo Features

### Access Demo Data Instantly

```bash
# Get all demo data
curl http://localhost:8000/api/v1/demo/all

# Individual datasets
curl http://localhost:8000/api/v1/demo/expenses
curl http://localhost:8000/api/v1/demo/marketing
curl http://localhost:8000/api/v1/demo/budgets
curl http://localhost:8000/api/v1/demo/forecasts
```

### Sample Data Included

**Expenses (6 transactions):**
- Slack ($1,500), Google Ads ($2,500), AWS ($800)
- Meta Ads ($3,000), Office Supplies ($450), HubSpot ($1,200)

**Marketing Campaigns (4):**
- Winter Sale (Facebook) - $5,000 - 250k impressions
- Product Launch (Google Ads) - $7,500 - 450k impressions
- Retargeting (Meta) - $3,000
- Email Newsletter - $500

**Budgets (4 departments):**
- Marketing: $235k annual
- Operations: $175k annual
- Engineering: $260k annual
- Sales: $150k annual

**Forecasts:** 3-month expense projections

## 🎨 Dashboard Pages

### Dashboard (`/`)
- Summary KPI cards (expenses, transactions, avg spend, marketing spend)
- Expense breakdown pie chart
- Marketing spend by platform
- Budget allocation by department with utilization bars
- Recent expenses table

### Expenses (`/expenses`)
- Full expense list with filtering
- Category breakdown
- Merchant tracking
- Total expenses and average transaction

### Budgets (`/budgets`)
- Department budget overview
- Quarterly breakdown
- Budget utilization percentage
- Health indicators (on-track, warning, exceeded)
- Budget alerts

### Marketing (`/marketing`) - Coming Soon
### Reports (`/reports`) - Coming Soon

## 🔧 Configuration

### Backend Configuration

Edit `app/.env`:

```env
# Demo/Presentation Mode (DEFAULT)
USE_SHEETS_FOR_DEMO=true
GOOGLE_SHEETS_ID=your_sheet_id
GOOGLE_SHEETS_OAUTH_TOKEN=your_token

# Production Mode
USE_SHEETS_FOR_DEMO=false

# Database
DATABASE_URL=sqlite+aiosqlite:///./finance_ai.db

# Logging
LOG_LEVEL=INFO

# API
API_HOST=0.0.0.0
API_PORT=8000
```

### Frontend Configuration

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_ENABLE_ANALYTICS=true
```

## 📚 API Documentation

### Interactive Docs

Open http://localhost:8000/docs in your browser for interactive Swagger UI.

### Key Endpoints

```
# Demo Data
GET  /api/v1/demo/all
GET  /api/v1/demo/expenses
GET  /api/v1/demo/marketing
GET  /api/v1/demo/budgets
GET  /api/v1/demo/forecasts

# Agents
POST /api/v1/expenses/sync         # Expense Collection Agent
GET  /api/v1/budgets/check         # Budget Monitoring Agent
GET  /api/v1/marketing/report      # Marketing Spend Agent
GET  /api/v1/dashboard             # Dashboard Agent

# Sheets Integration
POST /api/v1/sheets/auth/callback  # OAuth authentication
GET  /api/v1/sheets/status         # Check sheets status
POST /api/v1/sheets/demo-setup     # Demo instructions

# Health
GET  /api/v1/health                # Health check
```

## 🎯 Project Structure

```
finance-ai-server/
├── app/                          # Backend (FastAPI)
│   ├── src/
│   │   ├── agents/              # LangGraph agents
│   │   ├── api/                 # Route handlers
│   │   ├── application/         # Use cases
│   │   ├── domain/              # Business logic
│   │   ├── infrastructure/      # DB, connectors, auth
│   │   ├── core/                # Config, logging, exceptions
│   │   ├── schemas/             # Pydantic models
│   │   └── main.py              # App factory
│   ├── alembic/                 # DB migrations
│   ├── pyproject.toml           # Dependencies
│   └── Dockerfile               # Container image
├── frontend/                     # Frontend (React)
│   ├── src/
│   │   ├── pages/               # Route pages
│   │   ├── components/          # Reusable components
│   │   ├── lib/                 # Utilities (API client)
│   │   ├── styles/              # Global styles
│   │   └── types/               # TypeScript types
│   ├── package.json             # Dependencies
│   └── Dockerfile               # Container image
├── docker-compose.yml           # Multi-container orchestration
├── DEMO_MODE_QUICKSTART.md      # Quick demo guide
├── SHEETS_INTEGRATION.md        # Google Sheets setup
├── DOCKER_SETUP.md              # Docker documentation
└── SETUP_GUIDE.md               # This file
```

## 🔗 Integration Points

### Your APIs

When ready to integrate your own data sources:

1. **Create a connector** in `app/src/infrastructure/connectors/your_api.py`
2. **Implement Connector ABC interface** (4 methods: authenticate, fetch_transactions, get_source_name)
3. **Update agents** to use your connector
4. **Set `USE_SHEETS_FOR_DEMO=false`** in `.env`

Example:

```python
from src.infrastructure.connectors.base import Connector

class YourAPIConnector(Connector):
    async def authenticate(self) -> None:
        # Your auth logic
        pass
    
    async def fetch_transactions(self, company_id, start_date, end_date):
        # Fetch from your API
        transactions = []
        # ... populate
        return transactions
    
    async def get_source_name(self) -> str:
        return "Your API"
```

## 🚀 Deployment

### Deploy to Railway

```bash
# 1. Push to GitHub
git add .
git commit -m "Finance AI Server"
git push origin main

# 2. Connect to Railway
# https://railway.app
# Select GitHub repo
# Deploy!
```

### Deploy with Docker

```bash
# Build images
docker build -t finance-ai-backend:1.0.0 ./app
docker build -t finance-ai-frontend:1.0.0 ./frontend

# Push to registry
docker push your-registry/finance-ai-backend:1.0.0
docker push your-registry/finance-ai-frontend:1.0.0

# Update docker-compose.yml with image names and deploy
```

## 🔐 Security Checklist

- [ ] Change `SECRET_KEY` in settings
- [ ] Set `ENVIRONMENT=production` for production
- [ ] Enable HTTPS with reverse proxy (nginx)
- [ ] Store secrets in environment variables (never in code)
- [ ] Use strong database passwords
- [ ] Enable CORS for trusted domains only
- [ ] Rotate API keys regularly
- [ ] Use `.gitignore` to prevent secret leaks (✅ already set up)

## 📝 Troubleshooting

### Port Already in Use

```bash
# Kill process on port 8000 (backend)
lsof -ti :8000 | xargs kill -9

# Kill process on port 3000 (frontend)
lsof -ti :3000 | xargs kill -9

# Or use different ports
uvicorn src.main:app --port 8001
npm run dev -- -p 3001
```

### CORS Errors

```
Access to XMLHttpRequest at 'http://localhost:8000/api/v1/demo/all' 
from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Fix:** Backend already has CORS enabled. If still seeing issues:
1. Ensure backend is running
2. Check `CORS_ORIGINS` in `app/src/core/config/cors.py`
3. Restart both servers

### API Not Responding

```bash
# Check backend health
curl http://localhost:8000/api/v1/health

# Check frontend connection
curl -I http://localhost:3000

# View backend logs
tail -f app/logs/*.log
```

### Demo Data Not Loading

```bash
# Verify demo mode is enabled
grep USE_SHEETS_FOR_DEMO app/.env

# Ensure it's set to true
echo "USE_SHEETS_FOR_DEMO=true" >> app/.env

# Restart backend
```

## 📞 Support

### Documentation Files

- `DEMO_MODE_QUICKSTART.md` - Quick 2-minute demo
- `SHEETS_INTEGRATION.md` - Full Google Sheets setup
- `DOCKER_SETUP.md` - Docker & containerization
- `frontend/README.md` - Frontend development guide
- `app/src/main.py` - Backend application factory

### API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## ✨ Next Steps

1. **Start the application** (Docker or local)
2. **Explore the dashboard** at http://localhost:3000
3. **Try the demo endpoints** in Swagger UI
4. **Review sample data** structures
5. **Plan API integrations** for your data sources
6. **Customize UI** colors, branding, pages
7. **Deploy** to production

## 📊 Presentation Mode

Everything is optimized for presentations:

✅ **Demo data ready** - No setup needed, immediate data
✅ **Beautiful UI** - Professional dashboard with charts
✅ **Fast** - Sample data loads instantly
✅ **Offline** - Works without external API calls
✅ **Flexible** - Easy swap to real APIs later

Just start Docker and you're ready to present!

```bash
docker-compose up
# Demo runs at http://localhost:3000
```

---

**Version**: 0.1.0  
**Last Updated**: 2026-07-10  
**Project**: Finance AI Server - Recykal
