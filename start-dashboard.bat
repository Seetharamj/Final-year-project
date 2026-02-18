@echo off
REM Dashboard Startup Script - Windows Batch
REM Runs both the backend API server and frontend dashboard

echo ========================================================================
echo   Disaster Recovery Dashboard - Startup Script
echo ========================================================================

echo.
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo   X Python not found! Please install Python 3.9+
    pause
    exit /b 1
)
echo   √ Python found

echo.
echo [2/4] Activating virtual environment...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo   √ Virtual environment activated
) else (
    echo   ! Virtual environment not found. Creating one...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo   √ Virtual environment created and activated
)

echo.
echo [3/4] Installing dependencies...
pip install fastapi uvicorn websockets --quiet
echo   √ Dependencies ready

echo.
echo [4/4] Starting servers...
echo.
echo ========================================================================
echo   Starting Backend API Server (Port 5000)...
echo ========================================================================
start "Dashboard Backend API" cmd /k "cd /d %CD% && venv\Scripts\activate.bat && python dashboard\backend\api_server.py"

timeout /t 3 /nobreak >nul

echo.
echo ========================================================================
echo   Starting Frontend Dashboard (Port 8080)...
echo ========================================================================
start "Dashboard Frontend" cmd /k "cd /d %CD%\dashboard\frontend && python -m http.server 8080"

timeout /t 2 /nobreak >nul

echo.
echo ========================================================================
echo   Dashboard is now running!
echo ========================================================================
echo.
echo   Access Points:
echo   - Dashboard UI:    http://localhost:8080
echo   - Backend API:     http://localhost:5000
echo   - API Docs:        http://localhost:5000/docs
echo   - Health Check:    http://localhost:5000/health
echo.
echo   Features:
echo   - Real-time WebSocket updates
echo   - Click on any card to see detailed information
echo   - Interactive hazard monitoring
echo   - Multi-region status tracking
echo.
echo ========================================================================
echo   Opening dashboard in your browser...
echo ========================================================================
echo.

timeout /t 2 /nobreak >nul
start http://localhost:8080

echo.
echo   Dashboard is ready! Close the server windows to stop.
echo.
pause
