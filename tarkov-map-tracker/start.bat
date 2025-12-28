@echo off
echo ========================================
echo   Tarkov Map Tracker
echo ========================================
echo.

REM Check Python
echo Checking for Python...
where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.11+ from: https://www.python.org/
    pause
    exit /b 1
)
echo Python found!
echo.

REM First-time setup
if not exist "venv" (
    echo ========================================
    echo   FIRST TIME SETUP
    echo ========================================
    echo.
    echo This will take about 1-2 minutes...
    echo.
    
    echo [1/4] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo Done!
    echo.
    
    echo [2/4] Activating environment...
    call venv\Scripts\activate.bat
    echo Done!
    echo.
    
    echo [3/4] Upgrading pip...
    python -m pip install --upgrade pip --quiet
    echo Done!
    echo.
    
    echo [4/4] Installing dependencies...
    pip install -r requirements.txt --quiet
    echo Done!
    echo.
    
    echo ========================================
    echo   SETUP COMPLETE!
    echo ========================================
    echo.
    echo Everything is ready to go!
    echo Future launches will start instantly.
    echo.
    timeout /t 3 >nul
) else (
    call venv\Scripts\activate.bat
)

REM Launch the app
cls
echo ========================================
echo   Starting Tarkov Map Tracker
echo ========================================
echo.
echo Launching app...
echo Your browser will open automatically
echo.
echo Press Ctrl+C to stop the app
echo.
echo ========================================
echo.
streamlit run app.py

pause
