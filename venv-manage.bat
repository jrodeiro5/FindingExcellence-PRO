@echo off
REM ==================================================
REM FindingExcellence PRO - Virtual Environment Manager
REM ==================================================
REM This script manages the Python virtual environment for secure development
REM Usage: venv-manage.bat [install|update|audit|clean|help]

setlocal EnableDelayedExpansion

set PROJECT_ROOT=%~dp0
set VENV_PATH=%PROJECT_ROOT%venv
set REQUIREMENTS_PATH=%PROJECT_ROOT%backend\requirements.txt
set SCRIPT_NAME=%~nx0

echo.
echo ==================================================
echo   FindingExcellence PRO - Virtual Environment Manager
echo ==================================================
echo.

if "%1"=="" goto show_help

if "%1"=="install" goto install
if "%1"=="update" goto update
if "%1"=="audit" goto audit
if "%1"=="clean" goto clean
if "%1"=="help" goto show_help

echo ERROR: Unknown command '%1'
echo.
goto show_help

:install
echo [INFO] Installing virtual environment and dependencies...
echo.

REM Check Python installation
echo [STEP 1/5] Checking Python installation...
py --version >nul 2>&1
if !errorlevel! neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    goto error_exit
)

for /f "tokens=*" %%i in ('py --version') do set PYTHON_VERSION=%%i
echo Found: !PYTHON_VERSION!

REM Create virtual environment
echo.
echo [STEP 2/5] Creating virtual environment...
if exist "!VENV_PATH!" (
    echo Virtual environment already exists at !VENV_PATH!
    echo Removing existing environment...
    rmdir /s /q "!VENV_PATH!" >nul 2>&1
    if !errorlevel! neq 0 (
        echo ERROR: Failed to remove existing virtual environment
        goto error_exit
    )
)

py -3.13.3 -m venv "!VENV_PATH!"
if !errorlevel! neq 0 (
    echo ERROR: Failed to create virtual environment
    goto error_exit
)
echo Virtual environment created successfully with Python 3.13.3

REM Activate and upgrade pip
echo.
echo [STEP 3/5] Upgrading pip...
call "!VENV_PATH!\Scripts\activate.bat"
python -m pip install --upgrade pip >nul 2>&1
if !errorlevel! neq 0 (
    echo ERROR: Failed to upgrade pip
    goto error_exit
)
echo Pip upgraded successfully in Python 3.13.3 environment

REM Install dependencies
echo.
echo [STEP 4/5] Installing dependencies for Python 3.13.3...
if not exist "!REQUIREMENTS_PATH!" (
    echo ERROR: requirements.txt not found at !REQUIREMENTS_PATH!
    goto error_exit
)

pip install -r "!REQUIREMENTS_PATH!"
if !errorlevel! neq 0 (
    echo ERROR: Failed to install dependencies
    goto error_exit
)
echo Dependencies installed successfully

REM Install security tools
echo.
echo [STEP 5/5] Installing security tools...
pip install pip-audit safety >nul 2>&1
if !errorlevel! neq 0 (
    echo WARNING: Failed to install security tools
) else (
    echo Security tools installed successfully for Python 3.13.3
)

goto success_exit

:update
echo [INFO] Updating dependencies...
echo.

REM Check if virtual environment exists
if not exist "!VENV_PATH!" (
    echo ERROR: Virtual environment not found
    echo Run '%SCRIPT_NAME% install' first
    goto error_exit
)

REM Activate environment
call "!VENV_PATH!\Scripts\activate.bat"

REM Update pip first
echo [STEP 1/3] Updating pip...
python -m pip install --upgrade pip >nul 2>&1
echo Pip updated

REM Update all packages
echo.
echo [STEP 2/3] Updating packages...
pip list --outdated --format=freeze | findstr /R /C:"==" > outdated_packages.txt
if %errorlevel% equ 0 (
    echo Found outdated packages. Updating...
    for /f "tokens=1 delims==" %%i in (outdated_packages.txt) do (
        echo Updating %%i...
        pip install -U %%i >nul 2>&1
        if !errorlevel! equ 0 (
            echo   ✓ %%i updated
        ) else (
            echo   ✗ Failed to update %%i
        )
    )
    del outdated_packages.txt >nul 2>&1
) else (
    echo All packages are up to date
)

REM Update requirements file
echo.
echo [STEP 3/3] Updating requirements.txt...
pip freeze > "!REQUIREMENTS_PATH!"
echo requirements.txt updated

goto success_exit

:audit
echo [INFO] Running security audit...
echo.

REM Check if virtual environment exists
if not exist "!VENV_PATH!" (
    echo ERROR: Virtual environment not found
    echo Run '%SCRIPT_NAME% install' first
    goto error_exit
)

REM Activate environment
call "!VENV_PATH!\Scripts\activate.bat"

REM Check for dependency conflicts
echo [STEP 1/3] Checking for dependency conflicts...
pip check
if !errorlevel! neq 0 (
    echo WARNING: Dependency conflicts found
) else (
    echo No dependency conflicts found
)

REM Run security audit
echo.
echo [STEP 2/3] Running security audit with pip-audit...
pip-audit
set AUDIT_RESULT=!errorlevel!

REM Run additional security check
echo.
echo [STEP 3/3] Running additional security checks...
safety check --json 2>nul
if !errorlevel! neq 0 (
    echo Additional security issues found
) else (
    echo No additional security issues found
)

if !AUDIT_RESULT! neq 0 (
    echo.
    echo SECURITY WARNING: Vulnerabilities detected!
    echo Please review and update affected packages.
)

goto success_exit

:clean
echo [INFO] Cleaning virtual environment...
echo.

REM Check if virtual environment exists
if not exist "!VENV_PATH!" (
    echo Virtual environment not found - nothing to clean
    goto success_exit
)

REM Remove virtual environment
echo Removing virtual environment...
rmdir /s /q "!VENV_PATH!" >nul 2>&1
if !errorlevel! neq 0 (
    echo ERROR: Failed to remove virtual environment
    echo Please close any Python processes and try again
    goto error_exit
)

echo Virtual environment removed successfully
goto success_exit

:show_help
echo Usage: %SCRIPT_NAME% ^<command^>
echo.
echo Commands:
echo   install  - Create virtual environment and install dependencies
echo   update   - Update all packages and requirements.txt
echo   audit    - Run security audit and dependency checks
echo   clean    - Remove virtual environment completely
echo   help     - Show this help message
echo.
echo Examples:
echo   %SCRIPT_NAME% install
echo   %SCRIPT_NAME% audit
echo   %SCRIPT_NAME% update
echo.
goto exit

:success_exit
echo.
echo ==================================================
echo   Operation completed successfully!
echo ==================================================
echo.
goto exit

:error_exit
echo.
echo ==================================================
echo   Operation failed!
echo ==================================================
echo.
goto exit

:exit
endlocal
pause
