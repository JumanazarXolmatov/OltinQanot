# Oltin Qanot Bot Startup Script

# Stop any existing python processes to avoid conflicts
Write-Host "Stopping existing python processes..." -ForegroundColor Yellow
Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force

Write-Host "Starting Oltin Qanot Bot using .env configuration..." -ForegroundColor Green
python bot.py
