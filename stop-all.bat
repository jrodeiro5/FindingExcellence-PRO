@echo off
REM ==================================================
REM FindingExcellence PRO - Service Shutdown Script
REM ==================================================
REM This script stops all FindingExcellence services
REM Usage: stop-all.bat

echo.
echo ==================================================
echo   FindingExcellence PRO - Stopping All Services
echo ==================================================
echo.

echo Stopping Backend API Server (Python)...
taskkill /f /im python.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Backend server stopped
) else (
    echo ℹ️  No backend server found running
)

echo.
echo Stopping Frontend Development Server (Node.js)...
taskkill /f /im node.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Frontend server stopped
) else (
    echo ℹ️  No frontend server found running
)

echo.
echo Stopping any remaining service processes...
taskkill /f /fi "WINDOWTITLE eq FindingExcellence Backend" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq FindingExcellence Frontend" >nul 2>&1

echo.
echo Checking if services are still running...
echo.
echo Backend port 8000:
netstat -an | findstr ":8000" >nul
if %errorlevel% equ 0 (
    echo ⚠️  Port 8000 still in use - may need manual cleanup
) else (
    echo ✓ Port 8000 is free
)

echo Frontend port 5173:
netstat -an | findstr ":5173" >nul
if %errorlevel% equ 0 (
    echo ⚠️  Port 5173 still in use - may need manual cleanup
) else (
    echo ✓ Port 5173 is free
)

echo.
echo ==================================================
echo   Services Stopped Successfully!
echo ==================================================
echo.
echo All FindingExcellence PRO services have been stopped.
echo.
echo To restart services:
echo   start-all.bat     - Start all services in separate windows
echo   start-simple.bat  - Start all services in background
echo.
echo Press any key to close...
pause >nul
