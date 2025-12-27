@echo off
REM Tarkov Map Tracker - Windows Setup Script
REM Initializes git submodules and sets up Python environment

echo ================================
echo Tarkov Map Tracker Setup
echo ================================
echo.

REM Check if git is installed
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git is not installed or not in PATH
    echo Please install Git from https://git-scm.com/
    pause
    exit /b 1
)

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11 or later from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Initializing git repository...
if not exist ".git" (
    git init
    echo Git repository initialized
) else (
    echo Git repository already exists
)

echo.
echo [2/5] Adding git submodules for the-hideout repositories...
echo This may take a few minutes...

git submodule add https://github.com/the-hideout/TarkovMonitor.git vendor/TarkovMonitor 2>nul || echo TarkovMonitor submodule already exists
git submodule add https://github.com/the-hideout/tarkov-api.git vendor/tarkov-api 2>nul || echo tarkov-api submodule already exists
git submodule add https://github.com/the-hideout/tarkov-dev-svg-maps.git vendor/tarkov-dev-svg-maps 2>nul || echo tarkov-dev-svg-maps submodule already exists
git submodule add https://github.com/the-hideout/tarkov-dev.git vendor/tarkov-dev 2>nul || echo tarkov-dev submodule already exists

echo.
echo [3/5] Updating submodules...
git submodule update --init --recursive

echo.
echo [4/5] Creating Python virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)

echo.
echo [5/5] Installing Python dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ================================
echo Setup Complete!
echo ================================
echo.
echo Next steps:
echo 1. Edit config.yaml with your EFT paths
echo 2. Run the application:
echo    - Activate virtual environment: venv\Scripts\activate.bat
echo    - Start app: streamlit run app.py
echo.
echo For help, see README.md
echo.
pause
