@echo off
echo ========================================
echo AI-Driven Disaster Recovery System
echo Quick Start Guide
echo ========================================
echo.

echo [1/3] Setting up Python environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)

echo.
echo [2/3] Installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt

echo.
echo [3/3] Starting dashboard...
cd dashboard\frontend
start "Dashboard" python -m http.server 8080

echo.
echo ========================================
echo Dashboard is running at:
echo http://localhost:8080
echo ========================================
echo.
echo Opening browser...
timeout /t 2 /nobreak >nul
start http://localhost:8080

echo.
echo Press any key to exit...
pause >nul
