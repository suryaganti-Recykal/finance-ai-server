# Windows Quick Start - Get Dashboard Visible in 5 Minutes

## Prerequisites
- Python 3.12+ installed ([download](https://www.python.org/downloads/))
- Node.js 18+ installed ([download](https://nodejs.org/))
- Git (comes with most setups)

## Step 1: Open TWO PowerShell Windows

**Windows Key** → type `PowerShell` → Open **2 separate windows**

## Step 2: Start Backend (PowerShell Window #1)

```powershell
# Navigate to project
cd C:\Users\surya.ganti\finance-ai-server\app

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -e .

# Start backend server
uvicorn src.main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete
```

✅ **Don't close this window!**

---

## Step 3: Start Frontend (PowerShell Window #2)

```powershell
# Navigate to frontend
cd C:\Users\surya.ganti\finance-ai-server\frontend

# Install dependencies (first time only, takes 1-2 minutes)
npm install

# Create environment file
Copy-Item .env.example .env.local

# Start development server
npm run dev
```

**Expected output:**
```
- ready started server on 0.0.0.0:3000, url: http://localhost:3000
- event compiled client and server successfully
```

✅ **Don't close this window!**

---

## Step 4: Open Dashboard in Browser

1. **Open your web browser** (Chrome, Firefox, Edge, etc.)
2. **Go to:** http://localhost:3000
3. **You should see the Finance AI Dashboard!**

---

## What You Should See

### Dashboard Home Page (`/`)
- **Top Left:** Sidebar with links (Dashboard, Expenses, Budgets, etc.)
- **Top Right:** "Finance AI Dashboard" title
- **Main Content:**
  - 4 metric cards showing demo data
  - Pie chart of expenses by category
  - Bar chart of marketing spend
  - Budget breakdown table
  - Recent expenses

### If You See This ✅
Congratulations! Dashboard is working!

### If You See Blank Page or Error ❌
Follow troubleshooting below

---

## Troubleshooting

### "Cannot GET /"
**Problem:** Frontend not running

**Fix:**
- Check PowerShell Window #2
- Look for errors in the console
- Run: `npm install` again
- Run: `npm run dev`

### "Connection Refused" or "Not Responding"
**Problem:** One of the services isn't running

**Fix:** Check both PowerShell windows:
- Window #1: Should show "Uvicorn running on http://0.0.0.0:8000"
- Window #2: Should show "ready started server on 0.0.0.0:3000"

### Port Already in Use
**Problem:** Something else is using port 3000 or 8000

**Fix (Windows PowerShell as Admin):**
```powershell
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Kill process on port 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### Python Module Not Found
**Problem:** `ModuleNotFoundError: No module named 'src'`

**Fix:**
```powershell
# In app directory with activated venv
pip install -e .
```

### NPM Module Not Found
**Problem:** `Cannot find module`

**Fix:**
```powershell
# In frontend directory
rm -r node_modules
npm install
npm run dev
```

---

## Verify Everything Works

### Test Backend
Open another PowerShell and run:
```powershell
curl http://localhost:8000/api/v1/health
```

**Expected:** `{"status":"ok"}`

### Test Demo Data
```powershell
curl http://localhost:8000/api/v1/demo/all
```

**Expected:** JSON with expenses, marketing, budgets, forecasts

### Test API Documentation
Open browser to: http://localhost:8000/docs

**Expected:** Swagger UI with all API endpoints

---

## Dashboard Pages

Once dashboard is open, you can navigate to:

- **`/`** (Home) - Dashboard with KPIs and charts
- **`/expenses`** - Expense transaction list
- **`/budgets`** - Budget allocations by department
- **`/marketing`** - Marketing campaigns (coming soon)
- **`/reports`** - Monthly reports (coming soon)

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+C` in PowerShell | Stop the server |
| `Ctrl+R` in browser | Reload dashboard |
| `F12` in browser | Open developer console (for debugging) |

---

## If Still Having Issues

### Run the Verification Script
```powershell
cd C:\Users\surya.ganti\finance-ai-server
python verify_setup.py
```

This will check:
- Python version
- Node.js version
- Backend running
- Frontend running
- Demo data available

---

## Alternative: Use Docker (Easiest)

If you have Docker installed:

```powershell
# Navigate to project
cd C:\Users\surya.ganti\finance-ai-server

# Start everything with Docker
docker-compose up

# Open browser to http://localhost:3000
```

One command runs everything! No need for 2 PowerShell windows.

---

## Quick Reference

| What | Where | How |
|------|-------|-----|
| Dashboard | http://localhost:3000 | Browser |
| API Docs | http://localhost:8000/docs | Browser |
| Demo Data | http://localhost:8000/api/v1/demo/all | curl or browser |
| Stop Backend | PowerShell #1 | Ctrl+C |
| Stop Frontend | PowerShell #2 | Ctrl+C |
| Restart Backend | PowerShell #1 | Ctrl+C then run again |
| Restart Frontend | PowerShell #2 | Ctrl+C then `npm run dev` |

---

## Sample Data in Dashboard

**Expenses:** Slack, Google Ads, AWS, Meta Ads, Office Supplies, HubSpot  
**Total:** $9,450

**Marketing Campaigns:** Winter Sale, Product Launch, Retargeting, Email  
**Total Spend:** $15,500

**Budgets:** Marketing, Operations, Engineering, Sales  
**Total Annual:** $820,000

All sample data loads instantly in the dashboard!

---

## Need Help?

1. **Check PowerShell output** for error messages
2. **Check browser console** (F12) for JavaScript errors
3. **Run verification script** to identify the issue
4. **Check QUICK_FIX.md** for common solutions
5. **Try Docker** if local setup is problematic

---

## You're Set! 🎉

Once you see the dashboard loading:
- Explore the sample data
- Try different pages
- Check the API docs at /docs
- Prepare to integrate your own APIs

**Start time:** 5 minutes  
**Complexity:** Beginner-friendly  
**Cost:** Free (open source)

Happy building! 🚀
