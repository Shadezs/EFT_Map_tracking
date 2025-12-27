@echo off
REM Tarkov Map Tracker - One-Click Launcher
REM This script handles everything: setup, dependencies, and launching

echo ================================
echo Tarkov Map Tracker
echo ================================
echo.

REM Check Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.11+ from: https://www.python.org/
    pause
    exit /b 1
)

REM First-time setup
if not exist "venv" (
    echo First-time setup detected...
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing dependencies...
    python -m pip install --upgrade pip --quiet
    pip install -r requirements.txt --quiet
    echo Setup complete!
    echo.
) else (
    call venv\Scripts\activate.bat
)

REM Launch the app
echo Starting Tarkov Map Tracker...
echo.
echo The app will open in your browser automatically.
echo Press Ctrl+C to stop the app.
echo.
streamlit run app.py

pause
