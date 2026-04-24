@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [ERRO] Ambiente virtual nao encontrado em backend\.venv
  echo Rode a instalacao de dependencias do backend primeiro.
  pause
  exit /b 1
)

if not exist "run.py" (
  echo [ERRO] Ficheiro run.py nao encontrado em backend\
  pause
  exit /b 1
)

echo Iniciando backend...
call ".venv\Scripts\activate.bat"
python run.py

pause
