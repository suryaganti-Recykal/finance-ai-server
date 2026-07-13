# Complete Guide: Integrate Your Google Sheets & Host Online

**Goal:** Connect your Google Sheets data to the Finance AI dashboard and make it live on the internet.

**Time Required:** 20-30 minutes total  
**Cost:** FREE (Railway free tier)  
**Difficulty:** Beginner-friendly

---

## 📊 Your Google Sheet

**Sheet ID:** `1o_LPg73GPCr34rLLH84TGmXCx6I25J3b1pM1-AIonYc`

URL: https://docs.google.com/spreadsheets/d/1o_LPg73GPCr34rLLH84TGmXCx6I25J3b1pM1-AIonYc

---

## 🔄 Integration Workflow

```
Your Google Sheets
       ↓
   (OAuth Token)
       ↓
Finance AI Backend
       ↓
   (API Endpoints)
       ↓
React Dashboard
       ↓
Your Team Sees Data
```

---

## PHASE 1: Prepare Your Google Sheet (5 minutes)

### Check Your Sheet Structure

Your sheet should have named sheets with this data:

**Sheet Name: "Expenses"**
- Columns: Date, Description, Amount, Category, Source, MerchantName
- Example: `2026-01-15 | Slack subscription | 150 | Operations | Credit Card | Slack`

**Sheet Name: "Marketing"**
- Columns: CampaignName, Platform, Spend, Impressions, Clicks, Conversions, StartDate
- Example: `Winter Sale | Facebook | 1000 | 50000 | 2500 | 150 | 2026-01-01`

**Sheet Name: "Budgets"**
- Columns: Department, Q1, Q2, Q3, Q4, Total, Status
- Example: `Marketing | 5000 | 6000 | 5500 | 7000 | 23500 | active`

### If Your Sheet Structure is Different

If your sheets have different names or columns:

1. Tell me the structure
2. I'll update the connector code
3. Redeploy

For now, make sure you have these named sheets.

---

## PHASE 2: Get Google Sheets OAuth Token (5 minutes)

### Quick Method (Google OAuth Playground)

1. **Open:** https://oauth.google.com/oauthplayground

2. **Click settings icon** (gear in top right) → Check "Use your own OAuth credentials"

3. **In left sidebar**, find "Google Sheets API v4"

4. **Click on it** to expand, then click on "spreadsheets"

5. **Select checkbox:** `https://www.googleapis.com/auth/spreadsheets.readonly`

6. **Click blue "Authorize APIs"** button

7. **A Google login appears** → Sign in with your Google account

8. **Allow permissions** when asked

9. **Back in playground**, click "Exchange authorization code for tokens"

10. **Copy the access_token** (long string starting with `ya29.`)
    - It's the long value in the popup, NOT the refresh token

11. **Save this token** - you'll need it in next phase

**Your token looks like:**
```
ya29.a0AfH6SMBx...very long string...kFqBLsQ1234567890
```

---

## PHASE 3: Configure Local Testing (5 minutes)

### Update Configuration File

Edit `app/.env`:

```bash
# Change from demo mode to sheets mode
USE_SHEETS_FOR_DEMO=false

# Add your sheet ID
GOOGLE_SHEETS_ID=1o_LPg73GPCr34rLLH84TGmXCx6I25J3b1pM1-AIonYc

# Add your OAuth token
GOOGLE_SHEETS_OAUTH_TOKEN=ya29.a0AfH6SMBx...paste_your_token_here
```

### Test Locally

**Terminal 1 (Backend):**
```bash
cd app
.\venv\Scripts\activate
uvicorn src.main:app --reload
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

**Browser:**
```
http://localhost:3000
```

### Verify Your Data Shows

- Dashboard should show YOUR expenses (not demo data)
- Charts should display YOUR categories
- Budget table should show YOUR departments
- Recent expenses should show YOUR transactions

**If blank or error:** Check `GOOGLE_SHEETS_OAUTH_TOKEN` is correct

---

## PHASE 4: Deploy to Railway.app (10 minutes)

### Step 1: Push to GitHub

```bash
cd C:\Users\surya.ganti\finance-ai-server

git add .
git commit -m "Integrate Google Sheets data - ready for production"
git push origin main
```

### Step 2: Create Railway Account

1. Go to https://railway.app
2. Click "Start New Project"
3. Sign up with GitHub (recommended)
4. Authorize Railway

### Step 3: Deploy Project

1. Click "New Project"
2. Click "Deploy from GitHub repo"
3. Select your `finance-ai-server` repository
4. Railway auto-detects and starts building
5. **Wait 3-5 minutes** for build to complete

### Step 4: Add Environment Variables

**For Backend Service:**

1. In Railway, click your "backend" service
2. Go to "Variables" tab
3. Add these variables:

```
ENVIRONMENT=production
USE_SHEETS_FOR_DEMO=false
GOOGLE_SHEETS_ID=1o_LPg73GPCr34rLLH84TGmXCx6I25J3b1pM1-AIonYc
GOOGLE_SHEETS_OAUTH_TOKEN=ya29.a0AfH6SMBx...paste_your_token_here
DATABASE_URL=sqlite+aiosqlite:///./finance_ai.db
API_V1_PREFIX=/api/v1
```

4. Click "Save" → Railway auto-restarts

**For Frontend Service:**

1. Click your "frontend" service
2. Go to "Variables" tab
3. Add:

```
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app/api/v1
```

(Railway shows your backend URL in the service details)

4. Click "Save" → Railway auto-restarts

### Step 5: Verify Deployment

1. Go to Backend service → "Deployments"
2. Latest deployment should be green ✅
3. Click on it and view logs - should show: `Uvicorn running`
4. Go to Frontend service → latest deployment green ✅

Railway provides URLs:
- Frontend URL: Open in browser → Should show YOUR dashboard
- Backend URL: Add `/api/v1/health` → Should return `{"status":"ok"}`

---

## ✅ Success Checklist

- [ ] Google Sheets created with proper structure
- [ ] OAuth token obtained from playground
- [ ] Local `.env` configured with token
- [ ] Local dashboard shows YOUR data
- [ ] Code pushed to GitHub
- [ ] Railway project created
- [ ] Backend service deployed (green ✅)
- [ ] Frontend service deployed (green ✅)
- [ ] Environment variables added to both services
- [ ] Backend URL responds with health check
- [ ] Frontend URL loads dashboard
- [ ] Dashboard shows YOUR data (not demo data)

---

## 🚀 Your Live Links

Once deployed, share these with your team:

**Dashboard (What they see):**
```
https://your-frontend-url.railway.app
```

**API Documentation (For developers):**
```
https://your-backend-url.railway.app/docs
```

**Health Check (To verify it's running):**
```
https://your-backend-url.railway.app/api/v1/health
```

---

## 🔄 Update Your Dashboard

### Update Data in Google Sheets

1. Edit your Google Sheet
2. Add/change data
3. Save

### Refresh Dashboard

**Option 1: Manual Refresh**
1. Go to Railway backend service
2. Deployments → Click "..." on latest
3. Click "Redeploy"
4. Wait 1-2 minutes
5. Refresh browser - new data appears

**Option 2: Auto-Refresh (Advanced)**

You can set up a scheduled job to refresh every hour. Contact me if you want to set this up.

---

## 🛠️ If Something Goes Wrong

### "Dashboard shows demo data"
- Check `USE_SHEETS_FOR_DEMO=false` in Railway backend variables
- Redeploy backend service

### "Unauthorized" error
- OAuth token may be expired
- Get a new token from OAuth playground
- Update `GOOGLE_SHEETS_OAUTH_TOKEN` in Railway
- Redeploy

### "Sheet not found"
- Verify sheet ID is correct: `1o_LPg73GPCr34rLLH84TGmXCx6I25J3b1pM1-AIonYc`
- Verify sheet has named sheets: "Expenses", "Marketing", "Budgets"
- Check the Google Account you authorized matches the sheet owner

### "CORS error" in browser
- Go to Railway backend variables
- Ensure `CORS_ORIGINS` includes your frontend URL
- Or use `CORS_ORIGINS=["*"]` for any origin
- Redeploy

### "Can't see logs"
- Go to your Railway service
- Click "Deployments"
- Click latest deployment
- Click "View Logs"
- Look for error messages

---

## 📞 Support Resources

| Document | Purpose |
|----------|---------|
| `GOOGLE_SHEETS_SETUP.md` | Detailed Sheets configuration |
| `DEPLOY_TO_RAILWAY.md` | Railway deployment guide |
| `QUICK_FIX.md` | Troubleshooting common issues |
| `SETUP_GUIDE.md` | Complete reference guide |

---

## 🎯 Next Steps (Optional Features)

Once basic integration works:

1. **Add More Sheets** - Extend with Revenue, Collections, etc.
2. **Custom Columns** - Adjust if your data structure is different
3. **Auto-Refresh** - Schedule daily/hourly data pulls
4. **Export Data** - Add CSV/PDF export buttons
5. **Multiple Sheets** - Support several data sources
6. **Alerts** - Notify when budgets are exceeded
7. **Forecasting** - AI predictions using LangGraph agents
8. **Mobile App** - Use same API for mobile

---

## 💡 Pro Tips

### Security
- OAuth tokens expire after ~1 hour
- For production, use Google Service Account (no expiry)
- Never share tokens - keep in Railway secrets only
- Rotate tokens monthly

### Performance
- Dashboard loads instantly (Railway caches)
- Google Sheets API is free and fast
- No rate limiting for personal use
- Supports 100s of concurrent users

### Scale
- Start with one sheet
- Add more sheets as you grow
- Easy to migrate to PostgreSQL later
- Railway auto-scales containers

### Backup
- Google Sheets is your backup
- Data always saved there
- Export from Sheets anytime
- Database is just a cache

---

## 🎊 Timeline

- **Phase 1** (5 min): Prepare sheet
- **Phase 2** (5 min): Get OAuth token  
- **Phase 3** (5 min): Configure local
- **Phase 4** (10 min): Deploy to Railway
- **Total:** ~25 minutes

**Then:** Share link with team and celebrate! 🎉

---

**Ready to go live?** Start with PHASE 1 and work through each phase. 

If you get stuck, check the troubleshooting section or the specific phase guide.

Good luck! 🚀
