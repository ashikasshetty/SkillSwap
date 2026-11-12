@echo off
title SkillSwap Platform - Local Server
color 0B
cd /d "%~dp0"

echo ===================================================================
echo             SKILLSWAP - RECIPROCAL SKILL EXCHANGE
echo       MCA Mini Project - St Agnes College (Autonomous)
echo ===================================================================
echo.
echo [1/2] Preparing application server...
echo [2/2] Opening http://127.0.0.1:5000 in your default browser...
echo.

start "" cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:5000"

echo ===================================================================
echo  SkillSwap is LIVE at: http://127.0.0.1:5000
echo  Keep this console window open while using the platform.
echo  To shut down the server, simply close this window.
echo ===================================================================
echo.

py app.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo 'py' launcher not found. Trying 'python app.py'...
    python app.py
)

pause
