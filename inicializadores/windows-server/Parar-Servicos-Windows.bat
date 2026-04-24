@echo off
chcp 65001 >nul
net session >nul 2>&1
if errorlevel 1 (
  echo Execute como Administrador.
  pause
  exit /b 1
)

net stop EnvioApolices-Front 2>nul
net stop EnvioApolices-API 2>nul
echo Serviços parados ^(se existiam^).
pause
