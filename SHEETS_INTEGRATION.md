# Google Sheets Integration & Demo Mode

This guide explains how to configure the Finance AI agents to work with Google Sheets data for presentations and demonstrations.

## Quick Start: Demo Mode (No Setup Required)

By default, the agents run in **demo mode** with sample data. No configuration needed!

### Access Demo Data Endpoints

```bash
# Get all demo data at once
curl http://localhost:8000/api/v1/demo/all \
  -H "x-company-id: demo-company-001"

# Get specific data
curl http://localhost:8000/api/v1/demo/expenses
curl http://localhost:8000/api/v1/demo/marketing
curl http://localhost:8000/api/v1/demo/budgets
curl http://localhost:8000/api/v1/demo/forecasts
```

### What's Included in Demo Data

**Expenses:**
- Slack subscription ($1,500)
- Google Ads campaign ($2,500)
- AWS hosting ($800)
- Meta Ads ($3,000)
- Office supplies ($450)
- HubSpot CRM ($1,200)

**Marketing Campaigns:**
- Winter Sale (Facebook) - $5,000
- Product Launch (Google Ads) - $7,500
- Retargeting (Meta) - $3,000
- Email Newsletter - $500

**Budgets by Department:**
- Marketing: $235,000 annual
- Operations: $175,000 annual
- Engineering: $260,000 annual
- Sales: $150,000 annual

**Forecasts:** 3-month expense projections

## Setting Up Google Sheets Integration

To use **real Google Sheets** instead of demo data:

### Step 1: Create a Google Sheet

1. Visit https://sheets.google.com
2. Create a new spreadsheet
3. Copy the sheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit
                                           ^^^^^^^^^
   ```

### Step 2: Set Up Sheets with Data

Create 3 named sheets with these columns:

**Sheet: "Expenses"**
```
Date | Description | Amount | Category | Source | MerchantName
2026-01-15 | Slack subscription | 150 | Operations | Credit Card | Slack
2026-01-16 | Google Ads campaign | 500 | Marketing | Credit Card | Google
2026-01-17 | AWS hosting | 300 | Operations | Bank Transfer | AWS
```

**Sheet: "Marketing"**
```
CampaignName | Platform | Spend | Impressions | Clicks | Conversions | StartDate
Winter Sale | Facebook | 1000 | 50000 | 2500 | 150 | 2026-01-01
Product Launch | Google Ads | 1500 | 75000 | 3000 | 200 | 2026-01-10
```

**Sheet: "Budgets"**
```
Department | Q1 | Q2 | Q3 | Q4 | Total | Status
Marketing | 5000 | 6000 | 5500 | 7000 | 23500 | active
Operations | 10000 | 10000 | 10000 | 10000 | 40000 | active
```

### Step 3: Get Google OAuth Token

#### Option A: Using OAuth2 (Recommended for Presentations)

1. Open your browser and visit:
   ```
   https://accounts.google.com/o/oauth2/v2/auth?
   client_id=YOUR_CLIENT_ID&
   redirect_uri=http://localhost:8000/callback&
   response_type=code&
   scope=https://www.googleapis.com/auth/spreadsheets.readonly&
   access_type=offline
   ```

2. Approve access to Google Sheets

3. Copy the authorization code from the redirect

4. Exchange code for token:
   ```bash
   curl -X POST https://oauth2.googleapis.com/token \
     -d "code=AUTHORIZATION_CODE&client_id=YOUR_CLIENT_ID&client_secret=YOUR_SECRET&grant_type=authorization_code&redirect_uri=http://localhost:8000/callback"
   ```

5. Extract the `access_token` from the response

#### Option B: Using Service Account (For Automation)

1. Go to https://console.cloud.google.com
2. Create a new service account
3. Download the JSON key file
4. Share your Google Sheet with the service account email
5. Extract the access token from the JSON credentials

### Step 4: Configure the Backend

Set environment variables in `app/.env`:

```env
# Enable sheets for demo/presentation
USE_SHEETS_FOR_DEMO=true
GOOGLE_SHEETS_ID=YOUR_SHEET_ID_HERE
GOOGLE_SHEETS_OAUTH_TOKEN=YOUR_ACCESS_TOKEN_HERE
```

Or disable demo mode and use production connectors:

```env
USE_SHEETS_FOR_DEMO=false
```

### Step 5: Activate Sheets in API

Call the authentication endpoint:

```bash
curl -X POST http://localhost:8000/api/v1/sheets/auth/callback \
  -H "Content-Type: application/json" \
  -d '{
    "sheet_id": "YOUR_SHEET_ID",
    "oauth_token": "YOUR_ACCESS_TOKEN"
  }'
```

Check status:

```bash
curl http://localhost:8000/api/v1/sheets/status
```

## Running Agents with Demo/Sheets Data

### Expense Collection Agent

```bash
# Trigger expense collection (uses demo data by default)
curl -X POST http://localhost:8000/api/v1/expenses/sync \
  -H "x-company-id: demo-company-001"
```

Response includes:
- Transactions loaded from demo/sheets
- Duplicates removed
- Categories assigned
- Summary with counts

### Budget Monitoring Agent

```bash
curl -X GET http://localhost:8000/api/v1/budgets/check \
  -H "x-company-id: demo-company-001"
```

### Marketing Spend Agent

```bash
curl -X GET http://localhost:8000/api/v1/marketing/report \
  -H "x-company-id: demo-company-001"
```

### Dashboard Agent

```bash
curl -X GET http://localhost:8000/api/v1/dashboard \
  -H "x-company-id: demo-company-001"
```

## Switching Between Demo and Production

**Demo Mode (Default - Best for Presentations):**
```env
USE_SHEETS_FOR_DEMO=true
```
- Uses sample data
- No external APIs needed
- Fast, reliable, offline-capable

**Production Mode (Real APIs/Data):**
```env
USE_SHEETS_FOR_DEMO=false
```
- Uses configured connectors (Zoho, Meta, Google Ads, etc.)
- Requires API credentials for each service
- Real-time data

## Architecture

```
┌─────────────────┐
│  Frontend App   │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────┐
│  FastAPI Server                  │
├──────────────────────────────────┤
│  Routes:                         │
│  • /demo/all        (demo data)  │
│  • /sheets/auth/*   (OAuth)      │
│  • /expenses/sync   (agent)      │
│  • /budgets/*       (agent)      │
│  • /marketing/*     (agent)      │
└──────────────────────────────────┘
         │
         ▼
    ┌─────────────┐
    │  Agents     │
    │  (LangGraph)│
    └────┬────────┘
         │
    ┌────┴────────────────┬─────────────┐
    │                     │             │
    ▼                     ▼             ▼
┌─────────┐      ┌──────────────┐  ┌────────┐
│Demo Data│      │Google Sheets │  │Real    │
│Generator│      │(OAuth Token) │  │APIs    │
└─────────┘      └──────────────┘  └────────┘
```

## Troubleshooting

### "OAuth token not provided"
- Check `GOOGLE_SHEETS_OAUTH_TOKEN` is set in `.env`
- Re-authenticate via `/sheets/auth/callback`

### "Sheet not found"
- Verify sheet ID is correct
- Check sheet is shared with your OAuth account
- Named sheets must be: "Expenses", "Marketing", "Budgets"

### Agents still using real connectors
- Confirm `USE_SHEETS_FOR_DEMO=true` in `.env`
- Restart the server: `uvicorn app.src.main:app --reload`

### "No demo data available"
- Demo data is built-in, no setup needed
- If disabled, enable with `USE_SHEETS_FOR_DEMO=true`

## Integration with Your APIs

When you're ready to integrate your own APIs:

1. Keep `USE_SHEETS_FOR_DEMO=false`
2. Create new connector classes in `src/infrastructure/connectors/`
3. Follow the `Connector` ABC interface
4. Update agents to use your connectors
5. No changes needed to routes or agent logic

Example connector structure:

```python
from src.infrastructure.connectors.base import Connector, Transaction

class YourAPIConnector(Connector):
    async def authenticate(self) -> None:
        # Your auth logic
        pass
    
    async def fetch_transactions(self, company_id, start_date, end_date):
        # Your API call
        transactions = []
        # ... populate transactions
        return transactions
    
    async def get_source_name(self) -> str:
        return "Your API"
```

Then register in the agent's connector list!
