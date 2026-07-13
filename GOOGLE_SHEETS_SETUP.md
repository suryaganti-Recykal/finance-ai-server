# Google Sheets Integration & Deployment Guide

Your Sheet ID: `1o_LPg73GPCr34rLLH84TGmXCx6I25J3b1pM1-AIonYc`

---

## ⚡ Quick Steps (5 minutes)

### 1. Get Google OAuth Token

**Option A: Using Google Cloud Console (Recommended for Production)**

1. Go to https://console.cloud.google.com
2. Create a new project
3. Enable Google Sheets API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download JSON credentials
6. Extract the access token from the JSON

**Option B: Quick Test Token (For Development)**

1. Go to https://developers.google.com/sheets/api/quickstart/python
2. Click "Enable the Google Sheets API"
3. Create OAuth 2.0 credentials
4. Authorize and get token

---

## 📋 Sheet Structure Expected

Your sheet should have named sheets:

### Sheet 1: "Expenses"
```
Date | Description | Amount | Category | Source | MerchantName
2026-01-15 | Item | 150 | Category | Source | Merchant
```

### Sheet 2: "Marketing"
```
CampaignName | Platform | Spend | Impressions | Clicks | Conversions | StartDate
Campaign | Facebook | 1000 | 50000 | 2500 | 150 | 2026-01-01
```

### Sheet 3: "Budgets"
```
Department | Q1 | Q2 | Q3 | Q4 | Total | Status
Dept | 5000 | 6000 | 5500 | 7000 | 23500 | active
```

---

## 🔐 Configuration

### Step 1: Set Environment Variables

Edit `app/.env`:

```env
# Google Sheets
USE_SHEETS_FOR_DEMO=false
GOOGLE_SHEETS_ID=1o_LPg73GPCr34rLLH84TGmXCx6I25J3b1pM1-AIonYc
GOOGLE_SHEETS_OAUTH_TOKEN=your_access_token_here

# Or use service account
GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON={}
```

### Step 2: Get Your OAuth Token

**Manual Method (Quick):**

1. Visit: https://oauth.google.com/oauthplayground
2. In left sidebar, find "Google Sheets API v4"
3. Select scope: `https://www.googleapis.com/auth/spreadsheets.readonly`
4. Click "Authorize APIs"
5. Allow permissions
6. Click "Exchange authorization code for tokens"
7. Copy the **access_token** value
8. Paste into `GOOGLE_SHEETS_OAUTH_TOKEN=` in `.env`

---

## 🧪 Test Local Integration

### 1. Update Configuration

Edit `app/.env`:
```env
USE_SHEETS_FOR_DEMO=false
GOOGLE_SHEETS_ID=1o_LPg73GPCr34rLLH84TGmXCx6I25J3b1pM1-AIonYc
GOOGLE_SHEETS_OAUTH_TOKEN=your_token_here
```

### 2. Start Backend

```bash
cd app
uvicorn src.main:app --reload
```

### 3. Test the Connection

```bash
# Test health
curl http://localhost:8000/api/v1/health

# Get your sheet data
curl http://localhost:8000/api/v1/demo/all
```

**Expected Response:** JSON with your actual Sheets data

### 4. Check Dashboard

Open http://localhost:3000 → Should show YOUR data instead of demo data

---

## 🚀 Deploy to Production

### Option 1: Railway.app (Easiest - 5 minutes)

**Step 1: Push to GitHub**
```bash
git add .
git commit -m "Integrate Google Sheets data"
git push origin main
```

**Step 2: Deploy to Railway**

1. Go to https://railway.app
2. Sign up / Login
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repo
6. Railway auto-detects `Dockerfile` and `docker-compose.yml`
7. Add environment variables:
   - `GOOGLE_SHEETS_ID=1o_LPg73GPCr34rLLH84TGmXCx6I25J3b1pM1-AIonYc`
   - `GOOGLE_SHEETS_OAUTH_TOKEN=your_token`
   - `USE_SHEETS_FOR_DEMO=false`
   - `DATABASE_URL=postgresql://...` (Railway provides this)

**Step 3: Deploy**

Click "Deploy" and wait 2-5 minutes

Your app will be at: `https://your-app.up.railway.app`

---

### Option 2: Docker Hub + Any Host (More Control)

```bash
# 1. Build images
docker build -t yourusername/finance-ai-backend:1.0 ./app
docker build -t yourusername/finance-ai-frontend:1.0 ./frontend

# 2. Push to Docker Hub
docker push yourusername/finance-ai-backend:1.0
docker push yourusername/finance-ai-frontend:1.0

# 3. Create docker-compose-prod.yml on your host
# (similar to docker-compose.yml but with image URLs)

# 4. Run on your server
docker-compose -f docker-compose-prod.yml up -d
```

---

### Option 3: Heroku (Free Tier Ended, but still available)

```bash
# Install Heroku CLI
npm install -g heroku

# Login
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set GOOGLE_SHEETS_ID=1o_LPg73GPCr34rLLH84TGmXCx6I25J3b1pM1-AIonYc
heroku config:set GOOGLE_SHEETS_OAUTH_TOKEN=your_token
heroku config:set USE_SHEETS_FOR_DEMO=false

# Deploy
git push heroku main
```

---

### Option 4: AWS/GCP/Azure (Professional)

All support Docker containers. Follow their documentation to:
1. Push Docker images to their registry
2. Create container instances
3. Set environment variables
4. Point domain

---

## 🔄 Update Google Token (When Expires)

Google access tokens expire after ~1 hour. For long-term:

### Use Refresh Tokens

1. When getting OAuth token, request `refresh_token` too
2. Store both tokens
3. When access token expires, use refresh token to get new access token

### Or Use Service Account (Recommended for Production)

1. Create service account in Google Cloud Console
2. Generate JSON key
3. Share your Sheet with service account email
4. Use JWT authentication (doesn't expire)

---

## 📊 Sheet Configuration Examples

### If Your Sheet Has Different Column Names

Edit `app/src/infrastructure/connectors/google_sheets.py`:

```python
async def fetch_transactions(self, company_id, start_date, end_date):
    sheet_data = await self._read_sheet("Expenses")
    
    # Adjust column mapping based on YOUR sheet structure
    # Example if columns are: Date, Item, Cost, Type, Source, Business
    for row in sheet_data:
        transaction = Transaction(
            source="google_sheets",
            source_transaction_id=f"{self.sheet_id}_{row[0]}_{row[1][:20]}",
            amount=Decimal(str(row[2]).replace("$", "")),  # Cost column
            currency="USD",
            category=row[3],  # Type column
            description=row[1],  # Item column
            transaction_date=self._parse_date(row[0]),
            merchant=row[5],  # Business column
        )
```

---

## ✅ Deployment Checklist

- [ ] Google Sheets created with proper structure
- [ ] OAuth token obtained
- [ ] `GOOGLE_SHEETS_ID` added to `.env`
- [ ] `GOOGLE_SHEETS_OAUTH_TOKEN` added to `.env`
- [ ] `USE_SHEETS_FOR_DEMO=false` in `.env`
- [ ] Local test successful (see YOUR data in dashboard)
- [ ] Code pushed to GitHub
- [ ] Deployment platform set up (Railway/Heroku/Docker)
- [ ] Environment variables configured on platform
- [ ] App deployed and running
- [ ] Domain/URL shared with team

---

## 🎯 Next: Custom Sheet Mapping

If your sheet has different column names:

1. Take a screenshot of your sheet
2. Map columns to our expected format:
   - Date → transaction_date
   - Amount → amount
   - Category → category
   - Description → description

3. Update `google_sheets.py` with your column indices
4. Redeploy

---

## 🔗 Useful Links

- Google OAuth Playground: https://oauth.google.com/oauthplayground
- Railway.app: https://railway.app
- Google Cloud Console: https://console.cloud.google.com
- Docker Hub: https://hub.docker.com

---

## 🆘 Troubleshooting

### "Sheet not found"
- Verify sheet ID is correct
- Check sheet is shared (or service account has access)
- Verify named sheets exist: "Expenses", "Marketing", "Budgets"

### "Unauthorized" error
- Token may have expired
- Get new OAuth token from playground
- Update `.env` with new token

### "Empty data"
- Check sheet has data in correct format
- Verify column names match expected format
- Check date format is recognized (YYYY-MM-DD, MM/DD/YYYY, etc.)

### App deployed but showing demo data
- Verify `USE_SHEETS_FOR_DEMO=false` on platform
- Verify `GOOGLE_SHEETS_ID` and `GOOGLE_SHEETS_OAUTH_TOKEN` are set
- Restart containers

---

## 📝 Production Secrets Management

**NEVER put tokens in .env file in git!**

Use platform-specific secrets:
- Railway: Environment variables UI
- Heroku: `heroku config:set`
- AWS: Secrets Manager
- Docker: Environment files (not in git)

---

You're ready to integrate and deploy! 🚀
