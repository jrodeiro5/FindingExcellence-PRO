@echo off
REM Brand Asset Conversion Script
REM Converts Ayesa brand assets to required formats

echo ============================================================
echo AYESA BRAND ASSET CONVERTER
echo ============================================================
echo.

REM Check if venv is activated
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found
    echo Please run: uv-setup.bat
    exit /b 1
)

REM Run the conversion script
echo Running conversion script...
.venv\Scripts\python.exe scripts\convert_brand_assets.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Conversion failed
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Conversion completed successfully!
echo ============================================================
echo.
echo Generated assets are in: assets/
echo Asset index: assets/BRAND_ASSETS_INDEX.md
echo.
pause
