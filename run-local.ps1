# AI-Driven Cloud-Based Disaster Recovery System - Local Runner
# This script starts all components for local development

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI-Driven Disaster Recovery System" -ForegroundColor Cyan
Write-Host "Local Development Environment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-Not (Test-Path "venv")) {
    Write-Host "[1/5] Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "[1/5] Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "[2/5] Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Install dependencies if needed
Write-Host "[3/5] Checking Python dependencies..." -ForegroundColor Yellow
pip list | Select-String "scikit-learn" -Quiet
if (-Not $?) {
    Write-Host "Installing Python dependencies (this may take a few minutes)..." -ForegroundColor Yellow
    pip install -r requirements.txt
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✓ Dependencies already installed" -ForegroundColor Green
}

# Start AI Models in background
Write-Host "[4/5] Starting AI Models..." -ForegroundColor Yellow
Write-Host "  - Anomaly Detection (Isolation Forest)" -ForegroundColor Cyan
Write-Host "  - Service Degradation Predictor" -ForegroundColor Cyan

# Start Anomaly Detection
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; python ai-models\anomaly-detection\isolation-forest\detector.py" -WindowStyle Normal

# Wait a moment before starting next service
Start-Sleep -Seconds 2

# Start Degradation Predictor
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; python ai-models\prediction\degradation-predictor\predictor.py" -WindowStyle Normal

Write-Host "✓ AI Models started in separate windows" -ForegroundColor Green

# Start Dashboard
Write-Host "[5/5] Starting Dashboard..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\dashboard\frontend'; python -m http.server 8080" -WindowStyle Normal

Write-Host "✓ Dashboard server started" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "System is now running!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access the dashboard at: http://localhost:8080" -ForegroundColor Yellow
Write-Host ""
Write-Host "Components running:" -ForegroundColor White
Write-Host "  ✓ Anomaly Detection Model" -ForegroundColor Green
Write-Host "  ✓ Degradation Predictor" -ForegroundColor Green
Write-Host "  ✓ Dashboard (Port 8080)" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to open the dashboard in your browser..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Open browser
Start-Process "http://localhost:8080"

Write-Host ""
Write-Host "To stop all services, close the PowerShell windows." -ForegroundColor Yellow
