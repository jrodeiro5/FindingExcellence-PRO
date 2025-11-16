@echo off
REM ==================================================
REM FindingExcellence PRO - Simple Service Launcher
REM ==================================================
REM This script starts all services in the current window
REM Usage: start-simple.bat

echo.
echo ==================================================
echo   FindingExcellence PRO - Starting Services
echo ==================================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo ERROR: Virtual environment not found!
    echo.
    echo Please run the setup first:
    echo   venv-manage.bat install
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Verify activation
if "%VIRTUAL_ENV%"=="" (
    echo ERROR: Virtual environment activation failed!
    echo.
    pause
    exit /b 1
)

echo ✓ Virtual environment activated: %VIRTUAL_ENV%
echo.

REM Check if pnpm is available
pnpm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pnpm is not available!
    echo Please install pnpm: npm install -g pnpm
    echo.
    pause
    exit /b 1
)

echo ==================================================
echo   Service Information
echo ==================================================
echo.
echo Backend API:    http://127.0.0.1:8000
echo Frontend App:   http://localhost:5173
echo API Health:     http://127.0.0.1:8000/health
echo.
echo ==================================================
echo   Starting Services...
echo ==================================================
echo.

REM Start backend server
echo [1/2] Starting Backend API Server...
echo Backend running on: http://127.0.0.1:8000
echo.
start /B python backend\main.py

REM Wait for backend to initialize
echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Check backend status
curl -s http://127.0.0.1:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Backend is ready
) else (
    echo ⚠️  Backend may still be starting...
)

echo.

REM Start frontend server
echo [2/2] Starting Frontend Development Server...
echo Frontend running on: http://localhost:5173
echo.
start /B cmd /c "cd frontend && pnpm run dev"

REM Wait for frontend to initialize
echo Waiting for frontend to start...
timeout /t 5 /nobreak >nul

echo.
echo ==================================================
echo   Services Started!
echo ==================================================
echo.
echo ✓ Backend:  http://127.0.0.1:8000
echo ✓ Frontend: http://localhost:5173
echo.
echo Press Ctrl+C in this window to stop all services
echo.
echo Services are running in the background...
echo Use 'taskkill' commands to stop them manually:
echo   taskkill /f /im python.exe
echo   taskkill /f /im node.exe
echo.
echo Happy searching!
echo.

REM Keep script running
pause
