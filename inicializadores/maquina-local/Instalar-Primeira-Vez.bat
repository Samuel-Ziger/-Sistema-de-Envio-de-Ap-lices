@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0..\.."
set "ROOT=%CD%"

echo.
echo === Instalação (primeira vez) — Sistema de Envio de Apólices ===
echo Raiz do projeto: %ROOT%
echo.

where python >nul 2>&1
if errorlevel 1 (
  echo [Erro] Python não está no PATH. Instale Python 3.11+ e marque "Add to PATH".
  pause
  exit /b 1
)

where npm >nul 2>&1
if errorlevel 1 (
  echo [Erro] Node.js/npm não está no PATH. Instale Node.js LTS.
  pause
  exit /b 1
)

echo [1/4] Ambiente virtual do backend...
if not exist "%ROOT%\backend\.venv\Scripts\python.exe" (
  python -m venv "%ROOT%\backend\.venv"
)
call "%ROOT%\backend\.venv\Scripts\activate.bat"
python -m pip install --upgrade pip
pip install -r "%ROOT%\backend\requirements.txt"
if errorlevel 1 (
  echo [Erro] pip install falhou.
  pause
  exit /b 1
)

echo [2/4] Arquivo .env do backend...
if not exist "%ROOT%\backend\.env" (
  copy /Y "%ROOT%\backend\.env.example" "%ROOT%\backend\.env" >nul
  echo       Criado backend\.env a partir do exemplo. Edite SMTP_* antes de enviar e-mails.
)

echo [3/4] Dependências do frontend...
cd /d "%ROOT%\frontend"
if not exist "%ROOT%\frontend\.env" (
  copy /Y "%ROOT%\frontend\.env.example" "%ROOT%\frontend\.env" >nul
)
call npm install
if errorlevel 1 (
  echo [Erro] npm install falhou.
  pause
  exit /b 1
)

echo [4/4] Build de produção do painel (opcional, para modo preview)...
call npm run build
if errorlevel 1 (
  echo [Aviso] npm run build falhou; você ainda pode usar o modo desenvolvimento ^(Iniciar-Sistema.bat nesta pasta^).
)

cd /d "%ROOT%"
echo.
echo Pronto. Use Iniciar-Sistema.bat ou Iniciar-Sistema-Preview.bat nesta pasta ^(inicializadores\maquina-local^).
echo.
pause
