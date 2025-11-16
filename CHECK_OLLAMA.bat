@echo off
REM Check Ollama status and provide guidance

echo.
echo ========================================
echo Ollama Status Check
echo ========================================
echo.

echo Checking if Ollama is running...
curl -s http://localhost:11434/api/tags >nul 2>&1

if %errorlevel% equ 0 (
    echo ✅ Ollama is running!
    echo.
    echo Current models:
    curl -s http://localhost:11434/api/tags
    echo.
    echo Next: Download models using pull-models-fixed.bat
) else (
    echo ❌ Ollama is NOT running
    echo.
    echo Solution 1: Start Ollama from Windows Start Menu
    echo    1. Open Windows Start Menu
    echo    2. Search for "Ollama"
    echo    3. Click to start the application
    echo    4. Wait 30 seconds for it to start
    echo    5. Then run this script again: CHECK_OLLAMA.bat
    echo.
    echo Solution 2: Manual command (if installed)
    echo    Open Command Prompt and run:
    echo    ollama serve
    echo.
    echo Solution 3: Check installation
    echo    If Ollama isn't installed:
    echo    1. Download from: https://ollama.com
    echo    2. Run the installer
    echo    3. Restart your computer
    echo    4. Then try again
    echo.
)

pause
