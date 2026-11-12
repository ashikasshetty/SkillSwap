@echo off
title Push SkillSwap to GitHub
color 0A
cd /d "%~dp0"
set PATH=%LOCALAPPDATA%\MinGit\cmd;%PATH%

echo ===================================================================
echo             SKILLSWAP - GITHUB UPLOAD HELPER
echo ===================================================================
echo.
echo Local git repository is ready with all files committed on 'main'.
echo.
set /p REPO_URL="Enter your GitHub Repository URL (e.g. https://github.com/YourUsername/SkillSwap.git): "

if "%REPO_URL%"=="" (
    echo.
    echo [ERROR] No GitHub URL entered.
    pause
    exit /b
)

echo.
echo [1/3] Configuring remote origin to %REPO_URL%...
git remote remove origin 2>nul
git remote add origin %REPO_URL%

echo [2/3] Setting default branch to main...
git branch -M main

echo [3/3] Pushing project code to GitHub...
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ===================================================================
    echo  SUCCESS! SkillSwap repository has been uploaded to GitHub!
    echo ===================================================================
) else (
    echo.
    echo ===================================================================
    echo  If prompted, please enter your GitHub Personal Access Token
    echo  or GitHub credentials in the browser prompt.
    echo ===================================================================
)
echo.
pause

