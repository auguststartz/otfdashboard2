@echo off
REM RightFax Testing & Monitoring Platform - Windows Batch Script
REM This script launches the PowerShell startup script

echo ===============================================
echo RightFax Testing ^& Monitoring Platform
echo Windows Docker Desktop Edition
echo ===============================================
echo.

REM Check if PowerShell is available
where powershell >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: PowerShell is not available
    echo Please run start.ps1 directly with PowerShell
    pause
    exit /b 1
)

REM Run the PowerShell script
powershell -ExecutionPolicy Bypass -File "%~dp0start.ps1"

if %errorlevel% neq 0 (
    echo.
    echo Script execution failed
    pause
    exit /b 1
)
