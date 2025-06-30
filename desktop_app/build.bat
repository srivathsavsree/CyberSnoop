@echo off
REM CyberSnoop Desktop Application Build Script
REM This script builds the application for distribution

echo ==========================================
echo CyberSnoop Desktop Application Builder
echo ==========================================
echo.

REM Check if Python is available
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.11+ and try again.
    pause
    exit /b 1
)

echo [1/5] Checking virtual environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/5] Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo [4/5] Building frontend...
echo Frontend build will be implemented in Phase 3

echo [5/5] Creating executable...
echo Executable creation will be implemented in Phase 4

echo.
echo ==========================================
echo Build process completed successfully!
echo ==========================================
echo.
echo To run the application in development mode:
echo 1. Activate virtual environment: venv\Scripts\activate
echo 2. Run application: python cybersnoop_desktop.py
echo.
pause
