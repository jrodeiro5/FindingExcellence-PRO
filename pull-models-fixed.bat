@echo off
REM Pull required Ollama models for FindingExcellence PRO
REM This version handles Ollama installation path detection

echo.
echo ========================================
echo Finding Excellence PRO - Ollama Setup
echo ========================================
echo.

REM Try to find Ollama installation
echo Searching for Ollama installation...

REM Common Ollama installation paths
set OLLAMA_PATHS=^
"C:\Program Files\Ollama\ollama.exe" ^
"C:\Users\%USERNAME%\AppData\Local\Programs\Ollama\ollama.exe" ^
"%PROGRAMFILES%\Ollama\ollama.exe"

set OLLAMA_CMD=

for %%P in (%OLLAMA_PATHS%) do (
    if exist %%P (
        set OLLAMA_CMD=%%P
        echo Found Ollama at: %%P
        goto found_ollama
    )
)

:not_found
echo.
echo ERROR: Ollama not found in standard installation paths.
echo.
echo Please ensure Ollama is installed from: https://ollama.com
echo.
echo If Ollama is installed in a custom location, you can:
echo 1. Add Ollama to your Windows PATH environment variable
echo 2. Or manually run these commands:
echo.
echo    ollama pull llama3.1:8b
echo    ollama pull qwen2.5-vl:7b
echo    ollama pull deepseek-r1:1.5b
echo.
echo After downloading models, run: start-everything.bat
echo.
pause
exit /b 1

:found_ollama
echo ✅ Ollama found!
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file...
    (
        echo OLLAMA_HOST=http://localhost:11434
        echo OLLAMA_MODEL=llama3.1:8b
        echo OLLAMA_VISION_MODEL=qwen2.5-vl:7b
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
)

echo.
echo Step 1: Checking if Ollama service is running...
timeout /t 2 /nobreak

REM Check if Ollama API is responsive
for /f %%i in ('curl -s -o NUL -w "%%{http_code}" http://localhost:11434/api/tags') do set HTTP_CODE=%%i

if not "%HTTP_CODE%"=="200" (
    echo.
    echo ⚠️  Ollama service is not running!
    echo.
    echo Starting Ollama service...
    start "" "%OLLAMA_CMD%"
    echo Waiting for Ollama to start (10 seconds)...
    timeout /t 10 /nobreak
)

echo.
echo Step 2: Pulling llama3.1:8b (primary text model, ~4.7GB)...
"%OLLAMA_CMD%" pull llama3.1:8b
if %errorlevel% neq 0 (
    echo ERROR: Failed to pull llama3.1:8b
    pause
    exit /b 1
)

echo.
echo Step 3: Pulling qwen2.5-vl:7b (vision/OCR model, ~4.4GB)...
"%OLLAMA_CMD%" pull qwen2.5-vl:7b
if %errorlevel% neq 0 (
    echo ERROR: Failed to pull qwen2.5-vl:7b
    pause
    exit /b 1
)

echo.
echo Step 4: Pulling deepseek-r1:1.5b (fast fallback model, ~1GB)...
"%OLLAMA_CMD%" pull deepseek-r1:1.5b
if %errorlevel% neq 0 (
    echo WARNING: Failed to pull deepseek-r1:1.5b - continuing anyway
)

echo.
echo ========================================
echo Model Download Complete!
echo ========================================
echo.
echo Verifying models...
"%OLLAMA_CMD%" list

echo.
echo Next steps:
echo 1. Run: start-everything.bat
echo    (This will launch backend and frontend automatically)
echo.
echo 2. Or manually start each service:
echo    Terminal 1: activate.bat
echo    Terminal 1: python backend/main.py
echo    Terminal 2: cd frontend ^&^& pnpm run dev
echo.
echo 3. Open browser: http://localhost:5173
echo.
pause
