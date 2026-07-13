# Deploy Finance AI to Railway.app (Easiest Method)

Railway is the easiest way to deploy your app. **5 minutes, no credit card needed for free tier.**

---

## 🚀 Step-by-Step Deployment

### Step 1: Create Railway Account

1. Go to https://railway.app
2. Click "Start New Project"
3. Sign up with GitHub (easiest)
4. Authorize Railway to access your GitHub account

---

### Step 2: Prepare Your Project

Make sure everything is committed to Git:

```bash
cd C:\Users\surya.ganti\finance-ai-server

# Check status
git status

# If there are changes
git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

---

### Step 3: Deploy from GitHub

**In Railway dashboard:**

1. Click "New Project"
2. Click "Deploy from GitHub repo"
3. Select your repository: `finance-ai-server`
4. Railway auto-detects:
   - Backend: Dockerfile found
   - Frontend: Dockerfile found
   - Database: Optional (uses SQLite for now)

5. Click "Deploy"

**Wait 3-5 minutes for build to complete**

---

### Step 4: Add Environment Variables

Once deployed, Railway shows your services.

**For Backend Service:**

1. Click "Backend" service
2. Click "Variables" tab
3. Add these variables:

```
ENVIRONMENT=production
USE_SHEETS_FOR_DEMO=false
GOOGLE_SHEETS_ID=1o_LPg73GPCr34rLLH84TGmXCx6I25J3b1pM1-AIonYc
GOOGLE_SHEETS_OAUTH_TOKEN=your_token_here
DATABASE_URL=sqlite+aiosqlite:///./finance_ai.db
API_V1_PREFIX=/api/v1
CORS_ORIGINS=["*"]
```

Click "Save"

**For Frontend Service:**

1. Click "Frontend" service
2. Click "Variables" tab
3. Add:

```
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app/api/v1
```

(Railway will provide the backend URL)

---

### Step 5: Get Your Google Sheets OAuth Token

**Quick Method (5 minutes):**

1. Go to https://oauth.google.com/oauthplayground
2. Click settings icon (gear) → check "Use your own OAuth credentials"
3. In left sidebar, find "Google Sheets API v4"
4. Click on it, expand "spreadsheets"
5. Select: `https://www.googleapis.com/auth/spreadsheets.readonly`
6. Click blue "Authorize" button
7. Select your Google account
8. Click "Exchange authorization code for tokens"
9. Copy the **access_token** (long string starting with `ya29...`)
10. Paste into Railway backend variables: `GOOGLE_SHEETS_OAUTH_TOKEN=`

---

### Step 6: Verify Deployment

Railway gives you URLs:

- **Backend URL:** Something like `https://finance-ai-backend-prod.railway.app`
- **Frontend URL:** Something like `https://finance-ai-frontend-prod.railway.app`

**Test Backend:**
```
https://finance-ai-backend-prod.railway.app/api/v1/health
```

Should return: `{"status":"ok"}`

**Open Frontend in Browser:**
```
https://finance-ai-frontend-prod.railway.app
```

Should show your dashboard with YOUR Google Sheets data!

---

## ✅ Troubleshooting Deployment

### Dashboard Shows Demo Data Instead of My Data

**Problem:** `USE_SHEETS_FOR_DEMO` is still `true`

**Fix:**
1. Go to Railway backend service
2. Click "Variables"
3. Find `USE_SHEETS_FOR_DEMO`
4. Change to `false`
5. Click Save
6. Railway auto-restarts
7. Refresh dashboard

---

### "Unauthorized" or "Sheet not found"

**Problem:** OAuth token is wrong or expired

**Fix:**
1. Get new token from OAuth Playground (see above)
2. Update `GOOGLE_SHEETS_OAUTH_TOKEN` in Railway
3. Save and restart

---

### Dashboard Won't Load

**Check Logs:**
1. Go to Railway backend service
2. Click "Deployments" tab
3. Click latest deployment
4. Click "View Logs"
5. Look for error messages
6. Common fixes:
   - Missing environment variables (add them)
   - Token expired (get new one)
   - Sheet not accessible (check sharing)

---

### Can't Connect Backend from Frontend

**Problem:** Frontend gets CORS error

**Fix:**
1. Go to Railway backend service variables
2. Ensure: `CORS_ORIGINS=["*"]` or `CORS_ORIGINS=["https://your-frontend-url"]`
3. Go to Railway frontend service variables
4. Ensure: `NEXT_PUBLIC_API_URL=https://your-backend-url/api/v1` (with /api/v1 at end!)
5. Save both
6. Wait for restart
7. Refresh frontend

---

## 📊 Monitoring

### View Logs

1. Go to Backend service
2. Click "Deployments"
3. Click current deployment
4. Click "View Logs"
5. Look for errors or "Uvicorn running"

### View Metrics

1. Click service
2. "Metrics" tab
3. See CPU, memory, network usage

### Auto-Restart on Crash

Railway automatically restarts crashed services (built-in)

---

## 🔄 Update Your Data

To pull latest data from Google Sheets:

**Option 1: Automatic (Every Hour)**

You can set up a scheduled job to refresh. For now, data updates when app restarts.

**Option 2: Manual Refresh**

1. In Railway, go to Backend service
2. Click "Deployments"
3. Click three dots on latest deployment
4. Click "Redeploy"
5. App restarts and pulls fresh data

---

## 💰 Pricing

Railway free tier includes:
- **$5/month credit** (plenty for this app)
- Up to 2 services
- PostgreSQL/MySQL available (optional)
- Custom domain support
- Unlimited deployments

If you need more, paid plans start at $5/month.

---

## 🎯 Custom Domain (Optional)

To use your own domain (e.g., `finance-ai.yourcompany.com`):

1. In Railway service settings
2. Click "Domain"
3. Add custom domain
4. Railway gives you DNS records
5. Add records to your domain provider
6. Done!

---

## 🚨 Important: Secrets Management

**NEVER commit tokens to GitHub!**

Railway keeps them secret. But for extra safety:

1. Use short-lived tokens (1 hour)
2. Use refresh tokens for long-term
3. Rotate tokens monthly
4. Or use Google Service Account JWT (no expiry)

---

## 📈 Next Steps After Deploy

1. **Share the link** with your team
2. **Test with real data** - open the dashboard
3. **Monitor logs** for errors
4. **Update data** in Google Sheets, redeploy
5. **Customize** colors, add pages, export data
6. **Integrate more sheets** (Revenue, Collections, etc.)

---

## 💡 Pro Tips

### Auto-Deploy on Git Push

Railway auto-deploys when you push to GitHub:
1. Push to GitHub
2. Railway automatically pulls changes
3. Rebuilds Docker images
4. Restarts services
5. Live in 2-5 minutes

No manual deploys needed!

### Environment Secrets Safely

1. Create `.env.production` locally (not in git)
2. Copy variables into Railway UI
3. Never commit `.env.production`
4. Each team member can have different tokens if needed

### Backup Your Data

SQLite stores data in the container. For production:
1. Use PostgreSQL (Railway has free tier)
2. Or set up regular exports from Google Sheets
3. Update `DATABASE_URL` in Railway variables

---

## 🔗 Quick Links

- Railway Dashboard: https://railway.app/dashboard
- OAuth Playground: https://oauth.google.com/oauthplayground
- Your Google Sheet: https://docs.google.com/spreadsheets/d/1o_LPg73GPCr34rLLH84TGmXCx6I25J3b1pM1-AIonYc
- Docs: https://docs.railway.app

---

## 📝 Deployment Checklist

- [ ] GitHub account created and repo pushed
- [ ] Railway account created
- [ ] Project deployed from GitHub
- [ ] Environment variables added to Backend
- [ ] Environment variables added to Frontend
- [ ] Google Sheets OAuth token obtained
- [ ] Backend token configured
- [ ] Deployment build complete (green checkmark)
- [ ] Backend URL works (health check)
- [ ] Frontend URL opens in browser
- [ ] Dashboard shows YOUR data (not demo data)
- [ ] URL shared with team

---

## 🎉 You're Live!

Once all checks pass:

✅ Your Finance AI dashboard is live on the internet
✅ Data pulls from YOUR Google Sheets
✅ Team can access it anywhere
✅ Updates automatically when you redeploy
✅ Free to run (within free tier)

**Share this URL with your team:**
```
https://your-app.railway.app
```

---

**Questions?** Check logs, update environment variables, and redeploy. Railway makes it easy!
