@echo off
REM ==================================================
REM FindingExcellence PRO v2.0 - Unified Services Startup
REM ==================================================
REM Status: Updated December 31, 2025
REM - Branding: Ayesa corporate identity (blue #0000D0, pink #FF3184)
REM - File search: os.scandir + SQLite caching (3-5x faster, <10ms cached)
REM - Interactive results: sortable, copy paths, open files
REM - AI Analysis: Optimized (10-15s per document)
REM - All dependencies: backend + frontend + customtkinter

echo.
echo ==================================================
echo   FindingExcellence PRO v2.0 - Powered by Ayesa
echo   Starting Services
echo ==================================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo ERROR: Virtual environment not found!
    echo.
    echo Please run uv-setup.bat first to create the environment.
    echo.
    pause
    exit /b 1
)

REM Check if Ollama is running
echo Checking Ollama service...
timeout /t 2 /nobreak >nul
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Ollama may not be running at http://localhost:11434
    echo Please ensure Ollama is installed and started before continuing.
    echo.
    pause
)

REM Check dependencies
echo Checking dependencies...
.venv\Scripts\python.exe -c "import fastapi; import customtkinter; import pdfplumber; import requests" 2>nul
if errorlevel 1 (
    echo.
    echo ERROR: Missing required dependencies!
    echo.
    echo Please run: uv pip install -e .
    echo Or: uv pip install -r backend/requirements.txt
    echo Then: uv pip install -r frontend_desktop/requirements.txt
    echo.
    pause
    exit /b 1
)

REM Start backend server in a new window
echo.
echo Starting Backend Server (FastAPI on port 8000)...
echo - File search: Optimized with os.scandir + SQLite caching
echo - Models: phi4-mini (primary, fast CPU), qwen3:4b-instruct (fallback)
echo - Vision: deepseek-ocr (3B, 97%% accuracy)
echo - Status: http://localhost:8000/health
echo.
start "FindingExcellence Backend" cmd /k "cd /d %~dp0 && .venv\Scripts\python.exe backend\main.py"

REM Wait for backend to warm up (Ollama model warmup takes time)
echo Waiting for backend to initialize (this may take 30+ seconds for first model load)...
timeout /t 15 /nobreak >nul

REM Start frontend server in a new window
echo Starting Desktop Frontend...
echo - Interactive results: sortable columns, right-click menu, double-click open
echo - Performance: 3-5x faster file search, <10ms cached searches
echo.
start "FindingExcellence Frontend" cmd /k "cd /d %~dp0 && .venv\Scripts\python.exe frontend_desktop\main.py"

echo.
echo ==================================================
echo   Services Started Successfully!
echo ==================================================
echo.
echo Backend API:      http://127.0.0.1:8000
echo API Docs:         http://127.0.0.1:8000/docs
echo Health Check:     http://127.0.0.1:8000/health
echo.
echo Features:
echo   - Branding: Professional Ayesa corporate identity
echo   - File Search: os.scandir + SQLite caching (3-5x faster, ^<10ms cached)
echo   - Results: Interactive table, sortable, copy paths, open files, double-click open
echo   - AI Analysis: Optimized inference (10-15s per document)
echo   - Privacy: 100%% local - no external APIs, all models run locally
echo.
echo Keyboard:
echo   - Search Tab: Press Enter to start search
echo   - Results: Right-click for context menu, double-click to open
echo   - Columns: Click header to sort (▲▼)
echo.
echo To stop services: Run stop.bat or close both terminal windows
echo.
echo ==================================================
echo.
pause
