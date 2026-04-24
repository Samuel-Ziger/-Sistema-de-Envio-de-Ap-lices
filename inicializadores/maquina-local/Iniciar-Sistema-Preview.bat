@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0..\.."
set "ROOT=%CD%"

if not exist "%ROOT%\backend\.venv\Scripts\python.exe" (
  echo [Erro] Backend sem ambiente virtual. Execute primeiro: Instalar-Primeira-Vez.bat nesta pasta.
  pause
  exit /b 1
)
if not exist "%ROOT%\frontend\dist\index.html" (
  echo [Erro] Falta o build do frontend ^(frontend\dist^). Rode Instalar-Primeira-Vez.bat ou: cd frontend ^&^& npm run build
  pause
  exit /b 1
)

echo Abrindo API ^(8000^) e painel estático ^(5173 — vite preview^)...
start "Envio de Apólices — API" cmd /k "cd /d "%ROOT%\backend" && call .venv\Scripts\activate.bat && python run.py"
timeout /t 2 /nobreak >nul
start "Envio de Apólices — Painel" cmd /k "cd /d "%ROOT%\frontend" && npm run preview"
timeout /t 5 /nobreak >nul
start "" "http://localhost:5173"
echo Navegador aberto. Feche cada janela para encerrar.
timeout /t 3 /nobreak >nul
