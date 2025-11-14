# RightFax Testing & Monitoring Platform - Windows Startup Script
# PowerShell Script for Docker Desktop on Windows

# Change to the script's directory
Set-Location -Path $PSScriptRoot

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "RightFax Testing & Monitoring Platform" -ForegroundColor Cyan
Write-Host "Windows Docker Desktop Edition" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Working directory: $PSScriptRoot" -ForegroundColor Gray
Write-Host ""

# Check if Docker is installed and running
Write-Host "Checking Docker installation..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Docker not found"
    }
    Write-Host "[OK] Docker is installed: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Docker Desktop for Windows:" -ForegroundColor Yellow
    Write-Host "https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Docker daemon is running
Write-Host "Checking if Docker is running..." -ForegroundColor Yellow
try {
    docker ps > $null 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Docker daemon not running"
    }
    Write-Host "[OK] Docker is running" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker Desktop is not running" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please start Docker Desktop from the Start Menu" -ForegroundColor Yellow
    Write-Host "Wait for the Docker Desktop icon to show 'Docker is running'" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if .env file exists
Write-Host "Checking configuration..." -ForegroundColor Yellow

# Debug: List files in current directory
$envExists = Test-Path ".env"
$exampleExists = Test-Path ".env.example"
Write-Host "  .env file exists: $envExists" -ForegroundColor Gray
Write-Host "  .env.example file exists: $exampleExists" -ForegroundColor Gray

if (-not $envExists) {
    Write-Host "[WARNING] .env file not found" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Creating .env file from .env.example..." -ForegroundColor Yellow

    if ($exampleExists) {
        Copy-Item ".env.example" ".env"
        Write-Host "[OK] .env file created" -ForegroundColor Green
        Write-Host ""
        Write-Host "IMPORTANT: Please edit .env with your RightFax configuration:" -ForegroundColor Yellow
        Write-Host "  1. Open: notepad .env" -ForegroundColor White
        Write-Host "  2. Set RIGHTFAX_API_URL, RIGHTFAX_USERNAME, RIGHTFAX_PASSWORD" -ForegroundColor White
        Write-Host "  3. Set RIGHTFAX_FCL_DIRECTORY and RIGHTFAX_XML_DIRECTORY" -ForegroundColor White
        Write-Host "  4. Save and close Notepad" -ForegroundColor White
        Write-Host ""

        $response = Read-Host "Would you like to edit .env now? (Y/N)"
        if ($response -eq "Y" -or $response -eq "y") {
            notepad .env
            Write-Host "Waiting for you to save and close Notepad..." -ForegroundColor Yellow
        } else {
            Write-Host ""
            Write-Host "Please edit .env before running this script again" -ForegroundColor Red
            Write-Host ""
            Read-Host "Press Enter to exit"
            exit 1
        }
    } else {
        Write-Host "[ERROR] .env.example not found" -ForegroundColor Red
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "[OK] .env file found" -ForegroundColor Green
}

# Create necessary directories
Write-Host "Creating necessary directories..." -ForegroundColor Yellow
$directories = @("volumes\fcl", "volumes\xml", "logs", "uploads", "xml_archive")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "[OK] Created directory: $dir" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Starting Docker services..." -ForegroundColor Yellow
Write-Host ""

# Stop any existing containers
docker compose down 2>&1 | Out-Null

# Start services
docker compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] Failed to start Docker services" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting tips:" -ForegroundColor Yellow
    Write-Host "  1. Check that ports 80, 3000, 5000, 5432, 6379 are not in use" -ForegroundColor White
    Write-Host "  2. Ensure Docker Desktop has file sharing permissions" -ForegroundColor White
    Write-Host "  3. Check Docker Desktop logs for errors" -ForegroundColor White
    Write-Host "  4. Try running: docker compose logs" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service health
Write-Host ""
Write-Host "Checking service status..." -ForegroundColor Yellow
docker compose ps

Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "Platform Started Successfully!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access the application at:" -ForegroundColor Cyan
Write-Host "  - Web Interface:  http://localhost" -ForegroundColor White
Write-Host "  - Grafana:        http://localhost:3000 (admin/admin)" -ForegroundColor White
Write-Host "  - API:            http://localhost/api" -ForegroundColor White
Write-Host "  - Health Check:   http://localhost/health" -ForegroundColor White
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Cyan
Write-Host "  View logs:        docker compose logs -f" -ForegroundColor White
Write-Host "  Stop platform:    docker compose down" -ForegroundColor White
Write-Host "  Restart service:  docker compose restart web" -ForegroundColor White
Write-Host ""

# Optional: Open browser
$response = Read-Host "Would you like to open the web interface in your browser? (Y/N)"
if ($response -eq "Y" -or $response -eq "y") {
    Start-Process "http://localhost"
}

Write-Host ""
Write-Host "Press Enter to exit..."
Read-Host
