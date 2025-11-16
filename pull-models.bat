@echo off
REM Pull required Ollama models for FindingExcellence PRO
REM Run this in Command Prompt (not PowerShell)

echo.
echo ========================================
echo Finding Excellence PRO - Ollama Setup
echo ========================================
echo.
echo Pulling models from Ollama...
echo This may take 10-30 minutes depending on internet speed
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
echo Step 1: Pulling llama3.1:8b (primary text model, ~4.7GB)...
ollama pull llama3.1:8b
if %errorlevel% neq 0 (
    echo ERROR: Failed to pull llama3.1:8b
    pause
    exit /b 1
)

echo.
echo Step 2: Pulling qwen2.5-vl:7b (vision/OCR model, ~4.4GB)...
ollama pull qwen2.5-vl:7b
if %errorlevel% neq 0 (
    echo ERROR: Failed to pull qwen2.5-vl:7b
    pause
    exit /b 1
)

echo.
echo Step 3: Pulling deepseek-r1:1.5b (fast fallback model, ~1GB)...
ollama pull deepseek-r1:1.5b
if %errorlevel% neq 0 (
    echo WARNING: Failed to pull deepseek-r1:1.5b - continuing anyway
)

echo.
echo ========================================
echo Model Download Complete!
echo ========================================
echo.
echo Verifying models...
ollama list

echo.
echo Next steps:
echo 1. Activate venv: activate.bat
echo 2. Install dependencies: pip install -r backend/requirements.txt
echo 3. Start backend: python backend/main.py
echo 4. In another terminal: cd frontend && pnpm run dev
echo.
pause
