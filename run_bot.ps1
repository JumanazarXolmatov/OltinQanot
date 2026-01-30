# Run Oltin Qanot Bot
Set-Location -Path "oltin_qanot_bot"

if (-not (Test-Path ".env")) {
    Write-Host "Creating .env from example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "Please edit .env with your bot token!" -ForegroundColor Red
}

Write-Host "Starting Bot..." -ForegroundColor Green
python bot.py
