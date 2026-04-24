@echo off
chcp 65001 >nul
REM Inicia os serviços NSSM após instalação com installer\install.ps1 (como Administrador).
net session >nul 2>&1
if errorlevel 1 (
  echo Este ficheiro precisa ser executado como Administrador ^(botão direito — Executar como administrador^).
  pause
  exit /b 1
)

echo Iniciando EnvioApolices-API...
net start EnvioApolices-API
if errorlevel 1 (
  echo Falha ao iniciar API. O serviço está instalado? Rode installer\install.ps1 no servidor.
  pause
  exit /b 1
)

echo Iniciando EnvioApolices-Front...
net start EnvioApolices-Front
if errorlevel 1 (
  echo Aviso: frontend não iniciou ^(serviço opcional ou npx ausente na instalação^).
)

echo.
echo Pronto. API: http://localhost:8000/docs   Painel: http://localhost:5173
echo Ver também: inicializadores\windows-server\README.md
pause
