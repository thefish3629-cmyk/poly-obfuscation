@echo off
REM Polymarket Obfuscation Detection Pipeline Setup Script

echo ========================================
echo Polymarket Obfuscation Detector Setup
echo ========================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    exit /b 1
)

REM Check if Docker is available
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not in PATH
    exit /b 1
)

echo.
echo Step 1: Starting Docker containers...
docker compose up -d

echo.
echo Step 2: Waiting for databases to be ready...
timeout /t 10 /nobreak >nul

echo.
echo Step 3: Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Step 4: Copy .env.example to .env
if not exist .env (
    copy .env.example .env
    echo Created .env file - please edit it with your API keys
) else (
    echo .env already exists, skipping...
)

echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env and add your API keys
echo 2. Run: python -m src.main
echo.
