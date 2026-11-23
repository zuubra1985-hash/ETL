@echo off
cd /d "%~dp0"
echo ==========================================
echo   Uploading ARM ETL Android project to GitHub
echo   Repo: https://github.com/zuubra1985-hash/ETL.git
echo ==========================================
where git >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Git is not installed on this PC.
  echo Install Git from https://git-scm.com/download/win OR drag files into GitHub web UI.
  pause
  exit /b 1
)
if not exist ".git" git init
git config user.name "Dmitry Likhanov"
git config user.email "zuubra1985-hash@users.noreply.github.com"
git add -A
git commit -m "ARM ETL Android APK project" >nul 2>&1
git branch -M main
git remote remove origin >nul 2>&1
git remote add origin https://github.com/zuubra1985-hash/ETL.git
echo Pushing to GitHub (sign in via browser popup if asked)...
git push -u origin main --force
if errorlevel 1 (
  echo [ERROR] Push failed. Check GitHub login or upload files via web UI.
  pause
  exit /b 1
)
echo.
echo [OK] Project uploaded! Opening GitHub Actions to download APK...
start "" "https://github.com/zuubra1985-hash/ETL/actions"
pause
