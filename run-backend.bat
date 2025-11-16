@echo off
cd /d C:\Users\jrodeiro\Desktop\FindingExcellence_PRO

echo.
echo ========================================
echo FindingExcellence PRO - Backend Server
echo ========================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting backend server on port 8000...
echo.

python backend/main.py
