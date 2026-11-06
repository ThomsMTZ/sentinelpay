# One-click launcher for SentinelPay (Backend + Frontend)
Write-Host "Starting SentinelPay Backend (FastAPI on http://127.0.0.1:8000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PSScriptRoot\backend'; python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"

Write-Host "Starting SentinelPay Frontend (Vite on http://localhost:5173)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PSScriptRoot\frontend'; npm run dev"
