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
if not exist "%ROOT%\frontend\node_modules\" (
  echo [Erro] Frontend sem node_modules. Execute primeiro: Instalar-Primeira-Vez.bat nesta pasta.
  pause
  exit /b 1
)

echo Abrindo API ^(porta 8000^) e painel em modo desenvolvimento ^(porta 5173^)...
start "Envio de Apólices — API" cmd /k "cd /d "%ROOT%\backend" && call .venv\Scripts\activate.bat && python run.py"
timeout /t 2 /nobreak >nul
start "Envio de Apólices — Painel" cmd /k "cd /d "%ROOT%\frontend" && npm run dev"
timeout /t 6 /nobreak >nul
start "" "http://localhost:5173"
echo Navegador aberto. Feche cada janela preta para encerrar API ou painel.
timeout /t 3 /nobreak >nul
