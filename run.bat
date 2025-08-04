@echo off
echo Starting Image Search Application...
echo.

REM Change to script directory
cd /d "%~dp0"

REM Activate virtual environment if exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    echo.
)

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please run install_and_run.bat first
    pause
    exit /b 1
)

REM Create cache directory if not exists
if not exist "cache" (
    mkdir cache
)

REM Run the application
python main.py

if %errorlevel% neq 0 (
    echo.
    echo Application ended with error
    echo Check image_search.log for details
    pause
)

echo.
echo Application finished
pause