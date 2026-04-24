@echo off
REM Start manual do frontend em modo PREVIEW (usa dist/ já compilado)
cd /d "%~dp0..\frontend"
npm run preview
pause
