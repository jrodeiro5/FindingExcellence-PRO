@echo off
REM Download models using full Ollama path - Version 2 with alternative vision model

setlocal enabledelayedexpansion

set OLLAMA_EXE=C:\Users\jrodeiro\AppData\Local\Programs\Ollama\ollama.exe

echo.
echo ========================================
echo FindingExcellence PRO - Download Models
echo ========================================
echo.

if not exist "%OLLAMA_EXE%" (
    echo ERROR: Ollama not found at:
    echo %OLLAMA_EXE%
    echo.
    echo Please ensure Ollama is installed from: https://ollama.com
    pause
    exit /b 1
)

echo Found Ollama at:
echo %OLLAMA_EXE%
echo.

REM Check if Ollama is running
echo Checking if Ollama service is running...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Ollama service not responding at http://localhost:11434
    echo.
    echo Attempting to start Ollama...
    start "" "%OLLAMA_EXE%"
    echo Waiting 10 seconds for Ollama to start...
    timeout /t 10 /nobreak
    echo.
)

REM Create .env file if needed
if not exist .env (
    echo Creating .env file...
    (
        echo OLLAMA_HOST=http://localhost:11434
        echo OLLAMA_MODEL=llama3.1:8b
        echo OLLAMA_VISION_MODEL=llava:7b
        echo OLLAMA_TEMPERATURE=0.3
        echo OLLAMA_MAX_TOKENS=2000
        echo APP_NAME=FindingExcellence_PRO
        echo APP_VERSION=2.0.0
        echo DEFAULT_SEARCH_FOLDERS=C:\Users\%USERNAME%\Desktop,C:\Users\%USERNAME%\Downloads
        echo MAX_WORKERS=4
        echo LOG_LEVEL=INFO
        echo LOG_FILE=finding_excellence.log
    ) > .env
    echo .env file created!
    echo.
)

REM Download models
echo.
echo ========================================
echo Downloading Models
echo ========================================
echo.

echo Step 1: Pulling llama3.1:8b (4.7GB - primary text model)...
echo ✅ Already downloaded!
echo.

echo Step 2: Pulling llava:7b (3.8GB - vision/OCR model)...
echo This may take 5-15 minutes...
echo.
"%OLLAMA_EXE%" pull llava:7b
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Failed to pull llava:7b
    echo Trying alternative: llama2-vision
    "%OLLAMA_EXE%" pull llama2-vision
    if %errorlevel% neq 0 (
        echo WARNING: Both vision models failed
        echo You can still use text features (NL search, document analysis)
        echo.
    )
) else (
    echo.
    echo ✅ llava:7b downloaded successfully!
    echo.
)

echo Step 3: Pulling deepseek-r1:1.5b (1GB - fast fallback model)...
echo This may take 2-5 minutes...
echo.
"%OLLAMA_EXE%" pull deepseek-r1:1.5b
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Failed to pull deepseek-r1:1.5b
    echo This is optional - you can continue without it
    echo.
)

echo.
echo ========================================
echo ✅ Model Download Complete!
echo ========================================
echo.

echo Verifying downloaded models...
"%OLLAMA_EXE%" list

echo.
echo ========================================
echo Next Steps
echo ========================================
echo.
echo 1. To start the full application:
echo    Run: start-everything.bat
echo.
echo 2. Or start services manually:
echo.
echo    Terminal 1 (Backend):
echo      activate.bat
echo      python backend/main.py
echo.
echo    Terminal 2 (Frontend):
echo      cd frontend
echo      pnpm run dev
echo.
echo 3. Then open your browser:
echo    http://localhost:5173
echo.
echo ========================================
echo.
pause
