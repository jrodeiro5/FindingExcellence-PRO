@echo off
REM Start all services for FindingExcellence PRO with Ollama

title FindingExcellence PRO - Full Stack Start

echo.
echo ========================================
echo FindingExcellence PRO - Starting All Services
echo ========================================
echo.

REM Check if models are already downloaded
echo Checking for downloaded models...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  Ollama not responding. Please ensure Ollama is running.
    echo    Start Ollama from Windows Start Menu or run: ollama serve
    echo.
    pause
    exit /b 1
)

echo ✅ Ollama is running

REM Terminal 1: Models (only if not already downloaded)
echo.
echo Checking for models...
for /f %%i in ('curl -s http://localhost:11434/api/tags ^| find /c "llama3.1"') do set MODEL_CHECK=%%i

if %MODEL_CHECK% equ 0 (
    echo.
    echo 📥 Models not found. Downloading...
    echo    This will open in a new window and take 15-30 minutes
    echo.
    start "FindingExcellence - Model Download" cmd /k "title FindingExcellence - Model Download && cd /d C:\Users\%USERNAME%\Desktop\FindingExcellence_PRO && pull-models.bat && pause"
    echo.
    echo Please wait for models to download before continuing...
    echo (You can see progress in the 'Model Download' window)
    pause
) else (
    echo ✅ Models already downloaded
)

REM Terminal 2: Backend
echo.
echo 🚀 Starting Backend (Port 8000)...
start "FindingExcellence - Backend" cmd /k "title FindingExcellence - Backend && cd /d C:\Users\%USERNAME%\Desktop\FindingExcellence_PRO && activate.bat && python backend/main.py"

echo ⏳ Waiting 3 seconds for backend to start...
timeout /t 3 /nobreak

REM Terminal 3: Frontend
echo.
echo 🎨 Starting Frontend (Port 5173)...
start "FindingExcellence - Frontend" cmd /k "title FindingExcellence - Frontend && cd /d C:\Users\%USERNAME%\Desktop\FindingExcellence_PRO\frontend && pnpm run dev"

echo.
echo ========================================
echo ✅ All Services Started!
echo ========================================
echo.
echo 📍 Access your application:
echo    → http://localhost:5173
echo.
echo Windows opened:
echo    1. FindingExcellence - Model Download (if models needed)
echo    2. FindingExcellence - Backend (Port 8000)
echo    3. FindingExcellence - Frontend (Port 5173)
echo.
echo ⏳ Give the services 10-15 seconds to fully start before opening the browser.
echo.
echo 🔗 Once services are ready, open your browser and go to:
echo    http://localhost:5173
echo.
echo To stop everything, close the Windows or press Ctrl+C in each terminal.
echo.
pause
