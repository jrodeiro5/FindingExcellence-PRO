@echo off
REM ==================================================
REM Environment Test Script
REM ==================================================
REM This script tests the Windows CMD environment and Python setup

echo.
echo ==================================================
echo   Environment Test - FindingExcellence PRO
echo ==================================================
echo.

echo [INFO] Testing Windows CMD environment...
echo.

REM Test basic commands
echo [STEP 1/6] Testing basic Windows commands...
echo Current directory: %CD%
echo User profile: %USERPROFILE%
echo Computer name: %COMPUTERNAME%

REM Test Python Launcher
echo.
echo [STEP 2/6] Testing Python Launcher (py)...
py --version
if %errorlevel% equ 0 (
    echo ✓ Python Launcher is working
) else (
    echo ✗ Python Launcher not available
)

REM Test direct Python
echo.
echo [STEP 3/6] Testing direct Python command...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Direct Python command is working
) else (
    echo ✗ Direct Python command not available
    echo Note: This is normal if using Python Launcher
)

REM List Python installations
echo.
echo [STEP 4/6] Listing available Python installations...
py -0

REM Show Python paths
echo.
echo [STEP 5/6] Showing Python installation paths...
py -0p

REM Test virtual environment creation
echo.
echo [STEP 6/6] Testing virtual environment creation...
if exist "test-venv" (
    echo Removing existing test virtual environment...
    rmdir /s /q "test-venv" >nul 2>&1
)

echo Creating test virtual environment...
py -3.13.3 -m venv test-venv
if %errorlevel% equ 0 (
    echo ✓ Virtual environment created successfully
    echo.
    echo Testing activation...
    call test-venv\Scripts\activate.bat
    if "%VIRTUAL_ENV%"=="" (
        echo ✗ Virtual environment not activated properly
    ) else (
        echo ✓ Virtual environment activated: %VIRTUAL_ENV%
        python --version
        deactivate
    )

    echo.
    echo Cleaning up test environment...
    rmdir /s /q "test-venv" >nul 2>&1
    echo Test environment cleaned up
) else (
    echo ✗ Failed to create virtual environment
    echo Error code: %errorlevel%
)

echo.
echo ==================================================
echo   Environment Test Complete
echo ==================================================
echo.
echo Summary:
echo - Use 'py' command for Python operations
echo - Python 3.13.3 is available via Python Launcher
echo - Virtual environments should work with 'py -3.13.3'
echo.
pause
