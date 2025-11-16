@echo off
REM ==================================================
REM FindingExcellence PRO - Quick Activation Script
REM ==================================================
REM This script quickly activates the Python virtual environment
REM and sets up the development environment

echo.
echo ==================================================
echo   FindingExcellence PRO - Environment Activation
echo ==================================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo ERROR: Virtual environment not found!
    echo.
    echo Please run the setup first:
    echo   venv-manage.bat install
    echo.
    echo Note: Using Python Launcher (py) for Python 3.13.3
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment for Python 3.13.3...
call venv\Scripts\activate.bat

REM Verify activation
if not "%VIRTUAL_ENV%"=="" (
    echo Virtual environment activated: %VIRTUAL_ENV%
) else (
    echo WARNING: Virtual environment may not be activated properly
)

REM Show environment info
echo.
echo Environment Information:
python --version
pip --version

REM Check for security issues
echo.
echo Running quick security check...
pip check >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ No dependency conflicts
) else (
    echo ⚠️  Dependency conflicts found - run 'venv-manage.bat audit'
)

echo.
echo ==================================================
echo   Ready for Development!
echo ==================================================
echo.
echo Available commands:
echo   python backend\main.py    - Start the backend server
echo   venv-manage.bat audit     - Run security audit
echo   venv-manage.bat update    - Update dependencies
echo   deactivate                - Deactivate virtual environment
echo.
echo Note: Using Python 3.13.3 via Python Launcher
echo.
echo Happy coding!
echo.
