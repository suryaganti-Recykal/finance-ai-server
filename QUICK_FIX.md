# Quick Fix Guide - Dashboard Not Visible

## Step 1: Check if Services Are Running

### Backend Status
```bash
# Check if backend is running
curl http://localhost:8000/api/v1/health

# Expected response:
# {"status":"ok"}
```

If you get a connection error:
```bash
# Start backend
cd app
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
uvicorn src.main:app --reload
```

Wait for: `Uvicorn running on http://0.0.0.0:8000`

### Frontend Status
```bash
# Check if frontend is running
curl http://localhost:3000

# Should return HTML
```

If you get a connection error:
```bash
# Start frontend in NEW TERMINAL
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Wait for: `ready - started server on 0.0.0.0:3000`

---

## Step 2: Verify URLs

| Service | URL | Expected |
|---------|-----|----------|
| Frontend | http://localhost:3000 | Dashboard page |
| Backend API | http://localhost:8000 | Redirect to /docs |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Health Check | http://localhost:8000/api/v1/health | JSON: {"status":"ok"} |
| Demo Data | http://localhost:8000/api/v1/demo/all | JSON with demo data |

---

## Step 3: Check Logs for Errors

### Backend Logs
Look for errors like:
```
ERROR: Uvicorn not starting
ImportError: No module named 'src'
```

**Fix:**
```bash
cd app
pip install -e .
```

### Frontend Logs
Look for errors like:
```
Error: ENOENT: no such file or directory
Module not found: Can't resolve '@/lib/api'
```

**Fix:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## Step 4: Common Issues & Solutions

### Issue: "Cannot GET /"
**Cause:** Frontend not running

**Solution:**
```bash
cd frontend
npm run dev
```

---

### Issue: "Connection refused" on port 3000
**Cause:** Frontend not started or listening on different port

**Solution:**
```bash
# Check if something is using port 3000
lsof -i :3000  # macOS/Linux
netstat -ano | findstr :3000  # Windows

# Kill process if needed
kill -9 <PID>

# Start frontend
npm run dev
```

---

### Issue: CORS Error in Browser Console
**Error:** `Access to XMLHttpRequest from origin 'http://localhost:3000' blocked by CORS policy`

**Cause:** Backend CORS not configured

**Solution:** Backend CORS is already enabled. This usually means:
1. Backend is not running
2. API URL is incorrect in frontend `.env.local`

**Check:**
```bash
# Verify backend is running
curl http://localhost:8000/api/v1/health

# Check frontend .env.local
cat frontend/.env.local
# Should show: NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

### Issue: "Module not found" in frontend
**Error:** `Cannot find module '@/components/Layout'`

**Cause:** Node modules not installed

**Solution:**
```bash
cd frontend
rm -rf node_modules
npm install
npm run dev
```

---

### Issue: Python import errors
**Error:** `ModuleNotFoundError: No module named 'src'`

**Cause:** Not installed in editable mode

**Solution:**
```bash
cd app
pip install -e .
```

---

## Step 5: Full Fresh Start

If still not working, do a complete fresh install:

### Backend
```bash
cd app
rm -rf venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
uvicorn src.main:app --reload
```

### Frontend (NEW TERMINAL)
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

## Step 6: Verify Each Step

### 1. Backend Started?
```bash
curl http://localhost:8000/api/v1/health
# Should return: {"status":"ok"}
```

✅ If successful, move to step 2

### 2. Frontend Started?
```bash
curl http://localhost:3000
# Should return HTML (dashboard page)
```

✅ If successful, move to step 3

### 3. Open in Browser
```
http://localhost:3000
```

You should see the Finance AI dashboard with:
- Sidebar navigation (Dashboard, Expenses, Budgets, etc.)
- Header with "Finance AI Dashboard"
- KPI cards showing demo data
- Charts and tables

---

## Step 7: Debugging in Browser

### Open Developer Console
Press `F12` or `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Shift+I` (Mac)

### Check for Errors
Go to **Console** tab and look for red errors

### Check Network Requests
Go to **Network** tab and look for failed requests
- Should see: `GET /api/v1/demo/all` returning 200 status

### Check Application Storage
Go to **Application** tab → **Local Storage**
- Should see: `companyId: "demo-company-001"`

---

## Quick Checklist

- [ ] Backend running on port 8000?
- [ ] Frontend running on port 3000?
- [ ] Can access http://localhost:8000/api/v1/health?
- [ ] Can access http://localhost:3000 in browser?
- [ ] No red errors in browser console?
- [ ] Network requests showing 200 status?

If all ✅, you should see the dashboard!

---

## Still Not Working?

### Option A: Use Docker (Easiest)
```bash
docker-compose up --build
# Access at http://localhost:3000
```

### Option B: Get Help
Run this diagnostic:
```bash
# Backend check
curl -v http://localhost:8000/api/v1/health 2>&1

# Frontend check
curl -v http://localhost:3000 2>&1 | head -20

# Backend status
ps aux | grep uvicorn

# Frontend status
ps aux | grep "next dev"
```

Share the output and I can help!

---

## Expected Dashboard

When working correctly, you should see:

### Top Section
- Sidebar with navigation links
- Header with "Finance AI Dashboard"

### Main Content
- 4 KPI cards:
  - Total Expenses: $9,450
  - Transactions: 6
  - Avg Transaction: $1,575
  - Marketing Spend: $15,500

### Charts
- Pie chart: Expenses by Category
- Bar chart: Marketing by Platform

### Tables
- Budget allocation table
- Recent expenses table

If you see all this, **Dashboard is working!** ✅
