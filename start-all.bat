@echo off
REM ==================================================
REM FindingExcellence PRO - Unified Services Startup
REM ==================================================
REM This script starts all services (backend + frontend)
REM for the FindingExcellence PRO application

echo.
echo ==================================================
echo   FindingExcellence PRO - Starting All Services
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

echo Virtual environment activated: %VIRTUAL_ENV%
echo.

REM Check if backend is already running
echo Checking if backend is already running...
netstat -an | findstr ":8000" >nul
if %errorlevel% equ 0 (
    echo WARNING: Backend appears to be already running on port 8000
    echo.
) else (
    echo Backend port 8000 is available
    echo.
)

REM Check if frontend is already running
echo Checking if frontend is already running...
netstat -an | findstr ":5173" >nul
if %errorlevel% equ 0 (
    echo WARNING: Frontend appears to be already running on port 5173
    echo.
) else (
    echo Frontend port 5173 is available
    echo.
)

REM Start backend server in a new window
echo Starting Backend Server (FastAPI)...
echo Backend will run on: http://127.0.0.1:8000
echo.
start "FindingExcellence Backend" cmd /k "cd /d %~dp0 && call venv\Scripts\activate.bat && python backend\main.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend server in a new window
echo Starting Frontend Server (Vite + React)...
echo Frontend will run on: http://localhost:5173
echo.
start "FindingExcellence Frontend" cmd /k "cd /d %~dp0\frontend && pnpm run dev"

REM Wait a moment for frontend to start
timeout /t 3 /nobreak >nul

echo.
echo ==================================================
echo   Services Started Successfully!
echo ==================================================
echo.
echo Backend API:    http://127.0.0.1:8000
echo Frontend App:   http://localhost:5173
echo API Docs:       http://127.0.0.1:8000/docs
echo Health Check:   http://127.0.0.1:8000/health
echo.
echo ==================================================
echo   Service Management Commands
echo ==================================================
echo.
echo To stop services:
echo   - Close the backend window (Ctrl+C then close)
echo   - Close the frontend window (Ctrl+C then close)
echo.
echo To restart services:
echo   - Run this script again: start-all.bat
echo.
echo To check service status:
echo   - Backend: curl http://127.0.0.1:8000/health
echo   - Frontend: Open http://localhost:5173 in browser
echo.
echo ==================================================
echo   Security & Monitoring
echo ==================================================
echo.
echo Check security status:
echo   venv-manage.bat audit
echo.
echo View API usage stats:
echo   curl http://127.0.0.1:8000/api/usage/stats
echo.
echo ==================================================
echo   Ready to Use!
echo ==================================================
echo.
echo Open your browser to: http://localhost:5173
echo.
echo Press any key to close this window...
pause >nul
