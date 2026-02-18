# Dashboard Startup Script - Windows
# Runs both the backend API server and frontend dashboard

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host "  Disaster Recovery Dashboard - Startup Script" -ForegroundColor Green
Write-Host ("=" * 71) -ForegroundColor Cyan

# Check if Python is installed
Write-Host "`n[1/5] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Python found: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ Python not found! Please install Python 3.9+" -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "`n[2/5] Activating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
    Write-Host "  ✓ Virtual environment activated" -ForegroundColor Green
}
else {
    Write-Host "  ⚠ Virtual environment not found. Creating one..." -ForegroundColor Yellow
    python -m venv venv
    & "venv\Scripts\Activate.ps1"
    Write-Host "  ✓ Virtual environment created and activated" -ForegroundColor Green
}

# Install/check dependencies
Write-Host "`n[3/5] Checking dependencies..." -ForegroundColor Yellow
pip install fastapi uvicorn websockets --quiet
Write-Host "  ✓ Dependencies ready" -ForegroundColor Green

# Start backend API server
Write-Host "`n[4/5] Starting backend API server..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    param($projectPath)
    Set-Location $projectPath
    & "venv\Scripts\Activate.ps1"
    python dashboard\backend\api_server.py
} -ArgumentList (Get-Location).Path

Start-Sleep -Seconds 3

# Check if backend started successfully
if ($backendJob.State -eq "Running") {
    Write-Host "  ✓ Backend API server started on http://localhost:5000" -ForegroundColor Green
}
else {
    Write-Host "  ✗ Failed to start backend server" -ForegroundColor Red
    Receive-Job $backendJob
    exit 1
}

# Start frontend dashboard
Write-Host "`n[5/5] Starting frontend dashboard..." -ForegroundColor Yellow
$frontendJob = Start-Job -ScriptBlock {
    param($projectPath)
    Set-Location "$projectPath\dashboard\frontend"
    python -m http.server 8080
} -ArgumentList (Get-Location).Path

Start-Sleep -Seconds 2

if ($frontendJob.State -eq "Running") {
    Write-Host "  ✓ Frontend dashboard started on http://localhost:8080" -ForegroundColor Green
}
else {
    Write-Host "  ✗ Failed to start frontend server" -ForegroundColor Red
    Stop-Job $backendJob
    Remove-Job $backendJob
    exit 1
}

# Display success message
Write-Host "`n" -NoNewline
Write-Host ("=" * 71) -ForegroundColor Cyan
Write-Host "  🎉 Dashboard is now running!" -ForegroundColor Green
Write-Host ("=" * 71) -ForegroundColor Cyan

Write-Host "`n📊 Access Points:" -ForegroundColor Yellow
Write-Host "  • Dashboard UI:    " -NoNewline -ForegroundColor White
Write-Host "http://localhost:8080" -ForegroundColor Cyan
Write-Host "  • Backend API:     " -NoNewline -ForegroundColor White
Write-Host "http://localhost:5000" -ForegroundColor Cyan
Write-Host "  • API Docs:        " -NoNewline -ForegroundColor White
Write-Host "http://localhost:5000/docs" -ForegroundColor Cyan
Write-Host "  • Health Check:    " -NoNewline -ForegroundColor White
Write-Host "http://localhost:5000/health" -ForegroundColor Cyan

Write-Host "`n✨ Features:" -ForegroundColor Yellow
Write-Host "  • Real-time WebSocket updates" -ForegroundColor White
Write-Host "  • Click on any card to see detailed information" -ForegroundColor White
Write-Host "  • Interactive hazard monitoring" -ForegroundColor White
Write-Host "  • Multi-region status tracking" -ForegroundColor White

Write-Host "`n⌨️  Commands:" -ForegroundColor Yellow
Write-Host "  • Press Ctrl+C to stop all services" -ForegroundColor White
Write-Host "  • View backend logs: Receive-Job $($backendJob.Id)" -ForegroundColor White
Write-Host "  • View frontend logs: Receive-Job $($frontendJob.Id)" -ForegroundColor White

Write-Host "`n" -NoNewline
Write-Host ("=" * 71) -ForegroundColor Cyan
Write-Host "  Opening dashboard in your browser..." -ForegroundColor Green
Write-Host ("=" * 71) -ForegroundColor Cyan

# Open browser
Start-Sleep -Seconds 2
Start-Process "http://localhost:8080"

# Wait for user to stop
Write-Host "`nPress Ctrl+C to stop all services..." -ForegroundColor Yellow

try {
    while ($true) {
        Start-Sleep -Seconds 1
        
        # Check if jobs are still running
        if ($backendJob.State -ne "Running") {
            Write-Host "`n⚠ Backend server stopped unexpectedly!" -ForegroundColor Red
            Receive-Job $backendJob
            break
        }
        if ($frontendJob.State -ne "Running") {
            Write-Host "`n⚠ Frontend server stopped unexpectedly!" -ForegroundColor Red
            Receive-Job $frontendJob
            break
        }
    }
}
finally {
    # Cleanup
    Write-Host "`n`nStopping services..." -ForegroundColor Yellow
    Stop-Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
    Write-Host "✓ All services stopped" -ForegroundColor Green
}
