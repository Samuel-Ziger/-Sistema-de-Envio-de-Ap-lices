@echo off
setlocal

cd /d "%~dp0"

if not exist "package.json" (
  echo [ERRO] package.json nao encontrado em frontend\
  pause
  exit /b 1
)

if not exist "node_modules" (
  echo [INFO] Dependencias nao encontradas. Rodando npm install...
  npm install
  if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias do frontend.
    pause
    exit /b 1
  )
)

echo [INFO] Garantindo dependencias atualizadas...
npm install
if errorlevel 1 (
  echo [ERRO] Falha ao atualizar dependencias do frontend.
  pause
  exit /b 1
)

echo Iniciando frontend...
npm run dev

pause
