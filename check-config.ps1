# Quick Configuration Checker
# Shows what credentials are being used

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Configuration Checker" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Read .env file
Write-Host "Reading .env file..." -ForegroundColor Yellow
Write-Host ""

if (Test-Path ".env") {
    $postgresLines = Get-Content ".env" | Where-Object { $_ -match "POSTGRES" -and $_ -notmatch "^#" }

    Write-Host ".env file contents:" -ForegroundColor White
    $postgresLines | ForEach-Object { Write-Host "  $_" -ForegroundColor Green }

    Write-Host ""
    Write-Host "What the containers will see:" -ForegroundColor Yellow

    # Show what docker-compose will use
    docker compose config | Select-String -Pattern "POSTGRES" -Context 0,0 | ForEach-Object {
        Write-Host "  $_" -ForegroundColor Gray
    }
} else {
    Write-Host "[ERROR] .env file not found!" -ForegroundColor Red
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter to exit"
