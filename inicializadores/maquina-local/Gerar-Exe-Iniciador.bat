@echo off
chcp 65001 >nul
setlocal EnableExtensions
set "HERE=%~dp0"
cd /d "%HERE%..\.."
set "ROOT=%CD%"

if not exist "%ROOT%\backend\.venv\Scripts\python.exe" (
  echo Execute antes Instalar-Primeira-Vez.bat ^(nesta pasta^) para criar o Python em backend\.venv
  pause
  exit /b 1
)

call "%ROOT%\backend\.venv\Scripts\activate.bat"
pip install pyinstaller
if errorlevel 1 (
  echo Falha ao instalar pyinstaller.
  pause
  exit /b 1
)

if not exist "%HERE%dist-exe" mkdir "%HERE%dist-exe"
if not exist "%HERE%.pyinstaller-build" mkdir "%HERE%.pyinstaller-build"

pyinstaller --onefile --console --name IniciarEnvioApolices --clean --noconfirm ^
  --distpath "%HERE%dist-exe" --workpath "%HERE%.pyinstaller-build" --specpath "%HERE%" ^
  "%HERE%iniciar_tudo.py"
if errorlevel 1 (
  echo Falha no pyinstaller.
  pause
  exit /b 1
)

echo.
echo Executável: %HERE%dist-exe\IniciarEnvioApolices.exe
echo Coloque o .exe na RAIZ do projeto ^(ao lado de backend\ e frontend\^) para distribuir.
echo.
pause
