@echo off
setlocal

cd /d "%~dp0"

if not exist "package.json" (
  echo [ERRO] package.json nao encontrado em frontend\
  pause
  exit /b 1
)

if not exist "node_modules" (
  echo [ERRO] Dependencias nao encontradas em frontend\node_modules
  echo Rode npm install dentro da pasta frontend.
  pause
  exit /b 1
)

echo Iniciando frontend...
npm run dev

pause
