@echo off
REM ==================================================
REM FindingExcellence PRO - Direct CMD Setup
REM ==================================================
REM This script creates the virtual environment using direct Windows CMD commands
REM No Python Launcher dependencies - uses exact Python path

setlocal EnableDelayedExpansion

set PROJECT_ROOT=%~dp0
set PYTHON_PATH=C:\Users\jrodeiro\AppData\Local\Programs\Python\Python313\python.exe
set VENV_PATH=%PROJECT_ROOT%venv
set REQUIREMENTS_PATH=%PROJECT_ROOT%backend\requirements.txt

echo.
echo ==================================================
echo   FindingExcellence PRO - Direct CMD Setup
echo ==================================================
echo.

echo [INFO] Using direct Python path: %PYTHON_PATH%
echo.

REM Check if Python executable exists
if not exist "%PYTHON_PATH%" (
    echo ERROR: Python not found at expected location
    echo Please check Python installation at:
    echo %PYTHON_PATH%
    echo.
    pause
    exit /b 1
)

echo [STEP 1/4] Creating virtual environment...
if exist "%VENV_PATH%" (
    echo Removing existing virtual environment...
    rmdir /s /q "%VENV_PATH%" >nul 2>&1
    if !errorlevel! neq 0 (
        echo ERROR: Failed to remove existing virtual environment
        echo Please close any Python processes and try again
        pause
        exit /b 1
    )
)

"%PYTHON_PATH%" -m venv "%VENV_PATH%"
if !errorlevel! neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo ✓ Virtual environment created successfully

REM Activate and upgrade pip
echo.
echo [STEP 2/4] Upgrading pip...
call "%VENV_PATH%\Scripts\activate.bat"
python -m pip install --upgrade pip >nul 2>&1
if !errorlevel! neq 0 (
    echo WARNING: Failed to upgrade pip
) else (
    echo ✓ Pip upgraded successfully
)

REM Install dependencies
echo.
echo [STEP 3/4] Installing dependencies...
if not exist "%REQUIREMENTS_PATH%" (
    echo ERROR: requirements.txt not found at %REQUIREMENTS_PATH%
    pause
    exit /b 1
)

pip install -r "%REQUIREMENTS_PATH%"
if !errorlevel! neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed successfully

REM Install security tools
echo.
echo [STEP 4/4] Installing security tools...
pip install pip-audit safety >nul 2>&1
if !errorlevel! neq 0 (
    echo WARNING: Failed to install security tools
) else (
    echo ✓ Security tools installed successfully
)

echo.
echo ==================================================
echo   SETUP COMPLETE!
echo ==================================================
echo.
echo Virtual environment ready at: %VENV_PATH%
echo.
echo To activate the environment, run:
echo   venv\Scripts\activate.bat
echo.
echo Or use the quick activation script:
echo   activate.bat
echo.
echo Python version:
python --version
echo.
echo Ready for development!
echo.
pause
