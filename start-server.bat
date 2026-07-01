@echo off
setlocal enabledelayedexpansion

cd "C:\Users\surya.ganti\finance-ai-server\app"
set PYTHONPATH=C:\Users\surya.ganti\finance-ai-server\app;%PYTHONPATH%

echo.
echo ========================================
echo Finance AI Agent - Development Server
echo ========================================
echo.
echo Environment: development
echo Python: C:\Users\surya.ganti\finance-ai-server\venv\Scripts\python.exe
echo App Path: C:\Users\surya.ganti\finance-ai-server\app
echo.

"C:\Users\surya.ganti\finance-ai-server\venv\Scripts\python.exe" -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload

pause
