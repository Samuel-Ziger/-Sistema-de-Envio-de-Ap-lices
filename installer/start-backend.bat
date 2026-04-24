@echo off
REM Start manual do backend (para testes locais, sem serviço)
cd /d "%~dp0..\backend"
call .venv\Scripts\activate.bat
python run.py
pause
