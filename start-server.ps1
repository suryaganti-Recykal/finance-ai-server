cd "C:\Users\surya.ganti\finance-ai-server\app"
$env:PYTHONPATH = "C:\Users\surya.ganti\finance-ai-server\app;$env:PYTHONPATH"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Finance AI Agent - Development Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Environment: development" -ForegroundColor Green
Write-Host "Python: C:\Users\surya.ganti\finance-ai-server\venv\Scripts\python.exe" -ForegroundColor Green
Write-Host "App Path: C:\Users\surya.ganti\finance-ai-server\app" -ForegroundColor Green
Write-Host ""
Write-Host "Starting server..." -ForegroundColor Yellow
Write-Host ""

& "C:\Users\surya.ganti\finance-ai-server\venv\Scripts\python.exe" -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
