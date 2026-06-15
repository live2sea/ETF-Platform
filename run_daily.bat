@echo off
setlocal enabledelayedexpansion

set "PROJECT_DIR=D:\ETF-Platform"
set "VENV_PYTHON=%PROJECT_DIR%\venv\Scripts\python.exe"
set "LOG_DIR=%PROJECT_DIR%\logs"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
set "LOG_FILE=%LOG_DIR%\daily_batch.log"

echo ============================================>>"%LOG_FILE%"
echo ETF Daily Batch  %date% %time%>>"%LOG_FILE%"
echo ============================================>>"%LOG_FILE%"
echo.>>"%LOG_FILE%"

if not exist "%VENV_PYTHON%" (
    echo [ERROR] venv Python not found: %VENV_PYTHON%>>"%LOG_FILE%"
    exit /b 1
)

cd /d "%PROJECT_DIR%"
echo [INFO] Starting run_daily.py ...>>"%LOG_FILE%"
"%VENV_PYTHON%" "%PROJECT_DIR%\run_daily.py" 2>&1>>"%LOG_FILE%"
set "EXIT_CODE=%ERRORLEVEL%"

echo.>>"%LOG_FILE%"
echo ============================================>>"%LOG_FILE%"
if %EXIT_CODE% equ 0 (
    echo [OK] Batch completed successfully>>"%LOG_FILE%"
) else (
    echo [FAIL] Batch failed with exit code %EXIT_CODE%>>"%LOG_FILE%"
)
echo ============================================>>"%LOG_FILE%"

exit /b %EXIT_CODE%