@echo off
REM ==================================================
REM FindingExcellence PRO - Virtual Environment Setup
REM ==================================================
REM This script creates and activates a Python virtual environment
REM for secure dependency management and isolation.

echo.
echo ==================================================
echo   FindingExcellence PRO - Virtual Environment Setup
echo ==================================================
echo.

REM Check if Python is available
echo Checking Python installation...
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=*" %%i in ('py --version') do set PYTHON_VERSION=%%i
echo Found: %PYTHON_VERSION%

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo.
    echo Creating virtual environment...
    py -3.13 -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
) else (
    echo Virtual environment already exists
)

REM Activate the virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Verify activation
if not "%VIRTUAL_ENV%"=="" (
    echo Virtual environment activated: %VIRTUAL_ENV%
) else (
    echo WARNING: Virtual environment may not be activated properly
)

REM Upgrade pip to latest version
echo.
echo Upgrading pip to latest version...
python -m pip install --upgrade pip

REM Install dependencies from requirements.txt
echo.
echo Installing project dependencies...
if exist "backend\requirements.txt" (
    echo Installing from backend\requirements.txt...
    pip install -r backend\requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo Dependencies installed successfully
) else (
    echo WARNING: requirements.txt not found in backend directory
)

REM Run security audit
echo.
echo Running security audit...
pip-audit >nul 2>&1
if %errorlevel% equ 0 (
    echo Security audit completed
) else (
    echo WARNING: Security vulnerabilities found
    echo Run 'pip-audit' for details
)

REM Create .gitignore if it doesn't exist
if not exist ".gitignore" (
    echo.
    echo Creating .gitignore file...
    (
        echo venv/
        echo __pycache__/
        echo *.pyc
        echo *.pyo
        echo *.pyd
        echo .Python
        echo .env
        echo .vscode/
        echo .idea/
        echo *.log
        echo node_modules/
        echo dist/
        echo build/
        echo *.egg-info/
        echo .pytest_cache/
        echo .coverage
    ) > .gitignore
    echo .gitignore created
)

echo.
echo ==================================================
echo   Setup Complete!
echo ==================================================
echo.
echo Your virtual environment is ready to use.
echo The environment is automatically activated.
echo.
echo To reactivate in future sessions, run:
echo   venv\Scripts\activate.bat
echo.
echo To deactivate, run:
echo   deactivate
echo.
pause
