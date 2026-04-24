@echo off
REM Start manual do frontend em modo DEV (hot reload)
cd /d "%~dp0..\frontend"
npm run dev
pause
