# Database Connection Troubleshooting Script
# PowerShell Script to diagnose and fix PostgreSQL connection issues

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Database Connection Diagnostic Tool" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Check .env file
Write-Host "1. Checking .env configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    $envContent = Get-Content ".env" | Select-String -Pattern "POSTGRES"
    Write-Host "Current PostgreSQL settings in .env:" -ForegroundColor White
    $envContent | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
} else {
    Write-Host "[ERROR] .env file not found!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "2. Checking running containers..." -ForegroundColor Yellow
docker compose ps

Write-Host ""
Write-Host "3. Testing PostgreSQL container..." -ForegroundColor Yellow

# Get credentials from .env
$envVars = @{}
Get-Content ".env" | ForEach-Object {
    if ($_ -match "^\s*([^#][^=]+)=(.*)$") {
        $envVars[$matches[1].Trim()] = $matches[2].Trim()
    }
}

$dbUser = $envVars["POSTGRES_USER"]
$dbPassword = $envVars["POSTGRES_PASSWORD"]
$dbName = $envVars["POSTGRES_DB"]

Write-Host "Attempting to connect to PostgreSQL as user: $dbUser" -ForegroundColor Gray

# Test connection
$testResult = docker compose exec -T postgres psql -U $dbUser -d $dbName -c "SELECT version();" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Database connection successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Database is working correctly. The issue may be with environment variables" -ForegroundColor Yellow
    Write-Host "not being passed to the web container properly." -ForegroundColor Yellow
} else {
    Write-Host "[ERROR] Database connection failed!" -ForegroundColor Red
    Write-Host "Error: $testResult" -ForegroundColor Red
    Write-Host ""
    Write-Host "This indicates a password mismatch." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Recommended Fix" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "To fix this issue, follow these steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Stop all containers:" -ForegroundColor White
Write-Host "   docker compose down" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Remove the PostgreSQL volume:" -ForegroundColor White
Write-Host "   docker compose down -v" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Verify .env file has correct credentials:" -ForegroundColor White
Write-Host "   notepad .env" -ForegroundColor Gray
Write-Host ""
Write-Host "   Ensure these lines match:" -ForegroundColor White
Write-Host "   POSTGRES_USER=postgres" -ForegroundColor Gray
Write-Host "   POSTGRES_PASSWORD=YourPassword123" -ForegroundColor Gray
Write-Host "   POSTGRES_DB=rightfax_testing" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Start containers again:" -ForegroundColor White
Write-Host "   docker compose up -d" -ForegroundColor Gray
Write-Host ""
Write-Host "5. Wait 15 seconds for database to initialize" -ForegroundColor White
Write-Host ""
Write-Host "6. Check logs:" -ForegroundColor White
Write-Host "   docker compose logs web" -ForegroundColor Gray
Write-Host ""

$response = Read-Host "Would you like me to perform the fix automatically? (Y/N)"

if ($response -eq "Y" -or $response -eq "y") {
    Write-Host ""
    Write-Host "Performing automatic fix..." -ForegroundColor Yellow
    Write-Host ""

    Write-Host "Step 1: Stopping containers..." -ForegroundColor White
    docker compose down

    Write-Host "Step 2: Removing volumes..." -ForegroundColor White
    docker compose down -v

    Write-Host "Step 3: Starting containers with fresh database..." -ForegroundColor White
    docker compose up -d

    Write-Host "Step 4: Waiting for database to initialize (15 seconds)..." -ForegroundColor White
    Start-Sleep -Seconds 15

    Write-Host ""
    Write-Host "Step 5: Testing connection..." -ForegroundColor White
    $testResult2 = docker compose exec -T postgres psql -U $dbUser -d $dbName -c "SELECT 1;" 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Database connection successful!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Step 6: Checking web container..." -ForegroundColor White
        Start-Sleep -Seconds 5
        docker compose logs web --tail=30

        Write-Host ""
        Write-Host "[SUCCESS] Fix applied!" -ForegroundColor Green
        Write-Host "Try accessing http://localhost:8081 now" -ForegroundColor Cyan
    } else {
        Write-Host "[ERROR] Still having connection issues" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please check your .env file:" -ForegroundColor Yellow
        Write-Host "  notepad .env" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Make sure POSTGRES_USER and POSTGRES_PASSWORD are set correctly" -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "Manual fix not applied. Please follow the steps above manually." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press Enter to exit..."
Read-Host
