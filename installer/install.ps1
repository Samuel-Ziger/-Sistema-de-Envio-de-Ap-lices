<#
.SYNOPSIS
    Instalador completo do Sistema de Envio de Apolices para Windows Server.

.DESCRIPTION
    - Verifica/instala Python 3.11+ (usa winget se disponível, senão baixa do python.org)
    - Verifica/instala Node.js LTS (para build do frontend)
    - Instala NSSM (gerenciador de serviços Windows) em C:\tools\nssm
    - Cria virtualenv Python e instala requirements do backend
    - Faz npm install e build do frontend
    - Copia .env.example para .env (se não existir)
    - Adiciona as pastas de binários ao PATH do sistema
    - Copia inicializadores/ (atalhos .bat para máquina local e Windows Server)
    - Registra dois serviços Windows: EnvioApolices-API e EnvioApolices-Front (opcional)

.NOTES
    Execute como Administrador no Windows Server.

    Uso:
        Set-ExecutionPolicy -Scope Process Bypass -Force
        .\install.ps1
#>

[CmdletBinding()]
param(
    [string]$InstallDir = "C:\envio-sistema",
    [string]$ServicePort = "8000",
    [string]$FrontPort = "5173",
    [switch]$SkipFrontend,
    [switch]$SkipServices
)

$ErrorActionPreference = "Stop"

function Write-Step($msg)  { Write-Host "==> $msg" -ForegroundColor Cyan }
function Write-Ok($msg)    { Write-Host "[OK] $msg"    -ForegroundColor Green }
function Write-Warn($msg)  { Write-Host "[!]  $msg"    -ForegroundColor Yellow }
function Write-Err($msg)   { Write-Host "[X]  $msg"    -ForegroundColor Red }

function Assert-Admin {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    $p  = New-Object Security.Principal.WindowsPrincipal($id)
    if (-not $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Err "Este script precisa rodar como Administrador."
        exit 1
    }
}

function Test-Cmd($name) {
    return [bool](Get-Command $name -ErrorAction SilentlyContinue)
}

function Add-ToSystemPath($path) {
    $current = [Environment]::GetEnvironmentVariable("Path", "Machine")
    if ($current -notlike "*$path*") {
        Write-Step "Adicionando $path ao PATH do sistema"
        [Environment]::SetEnvironmentVariable("Path", "$current;$path", "Machine")
        # Atualiza a sessão atual também
        $env:Path = "$env:Path;$path"
        Write-Ok "PATH atualizado"
    } else {
        Write-Ok "$path já está no PATH"
    }
}

function Install-Python {
    if (Test-Cmd python) {
        $ver = (python --version) 2>&1
        Write-Ok "Python já instalado: $ver"
        return
    }
    Write-Step "Python não encontrado, instalando..."
    if (Test-Cmd winget) {
        winget install -e --id Python.Python.3.11 --accept-package-agreements --accept-source-agreements
    } else {
        $url = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
        $out = "$env:TEMP\python-installer.exe"
        Invoke-WebRequest -Uri $url -OutFile $out
        Start-Process -FilePath $out -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_pip=1" -Wait
    }
    Write-Ok "Python instalado"
}

function Install-Node {
    if (Test-Cmd node) {
        $ver = (node --version) 2>&1
        Write-Ok "Node já instalado: $ver"
        return
    }
    Write-Step "Node.js não encontrado, instalando..."
    if (Test-Cmd winget) {
        winget install -e --id OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements
    } else {
        $url = "https://nodejs.org/dist/v20.18.0/node-v20.18.0-x64.msi"
        $out = "$env:TEMP\node-installer.msi"
        Invoke-WebRequest -Uri $url -OutFile $out
        Start-Process -FilePath "msiexec.exe" -ArgumentList "/i `"$out`" /qn /norestart" -Wait
    }
    Write-Ok "Node.js instalado"
}

function Install-NSSM {
    $tools = "C:\tools"
    $nssmDir = Join-Path $tools "nssm"
    $nssmExe = Join-Path $nssmDir "nssm.exe"

    if (Test-Path $nssmExe) {
        Write-Ok "NSSM já instalado em $nssmExe"
        Add-ToSystemPath $nssmDir
        return $nssmExe
    }

    Write-Step "Instalando NSSM em $nssmDir"
    New-Item -ItemType Directory -Path $nssmDir -Force | Out-Null
    $zip = Join-Path $env:TEMP "nssm.zip"
    Invoke-WebRequest -Uri "https://nssm.cc/release/nssm-2.24.zip" -OutFile $zip
    $tmpExtract = Join-Path $env:TEMP "nssm-extract"
    if (Test-Path $tmpExtract) { Remove-Item -Recurse -Force $tmpExtract }
    Expand-Archive -Path $zip -DestinationPath $tmpExtract -Force

    $src = Get-ChildItem -Path $tmpExtract -Recurse -Filter "nssm.exe" |
           Where-Object { $_.FullName -like "*win64*" } | Select-Object -First 1
    if (-not $src) {
        $src = Get-ChildItem -Path $tmpExtract -Recurse -Filter "nssm.exe" | Select-Object -First 1
    }
    Copy-Item $src.FullName $nssmExe -Force
    Add-ToSystemPath $nssmDir
    Write-Ok "NSSM instalado"
    return $nssmExe
}

function Deploy-Sources {
    Write-Step "Copiando fontes para $InstallDir"
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null

    $root = Split-Path $PSScriptRoot -Parent   # pasta envio-sistema
    Copy-Item -Path (Join-Path $root "backend")   -Destination $InstallDir -Recurse -Force
    if (-not $SkipFrontend) {
        Copy-Item -Path (Join-Path $root "frontend") -Destination $InstallDir -Recurse -Force
    }
    $ini = Join-Path $root "inicializadores"
    if (Test-Path $ini) {
        Copy-Item -Path $ini -Destination $InstallDir -Recurse -Force
    }
    Copy-Item -Path $PSScriptRoot -Destination $InstallDir -Recurse -Force

    # .env
    $envExample = Join-Path $InstallDir "backend\.env.example"
    $envFile    = Join-Path $InstallDir "backend\.env"
    if (-not (Test-Path $envFile) -and (Test-Path $envExample)) {
        Copy-Item $envExample $envFile
        Write-Ok "Criado backend\.env (ajuste SMTP antes de iniciar)"
    }

    if (-not $SkipFrontend) {
        $feEnvEx = Join-Path $InstallDir "frontend\.env.example"
        $feEnv   = Join-Path $InstallDir "frontend\.env"
        if (-not (Test-Path $feEnv) -and (Test-Path $feEnvEx)) {
            Copy-Item $feEnvEx $feEnv
        }
    }
}

function Setup-BackendEnv {
    $backend = Join-Path $InstallDir "backend"
    Push-Location $backend
    try {
        Write-Step "Criando virtualenv Python"
        python -m venv .venv
        $pip = Join-Path $backend ".venv\Scripts\pip.exe"
        $py  = Join-Path $backend ".venv\Scripts\python.exe"

        Write-Step "Atualizando pip"
        & $py -m pip install --upgrade pip

        Write-Step "Instalando dependências Python"
        & $pip install -r requirements.txt

        Write-Ok "Backend preparado"
    } finally { Pop-Location }
}

function Build-Frontend {
    if ($SkipFrontend) { Write-Warn "Frontend ignorado (-SkipFrontend)"; return }
    $front = Join-Path $InstallDir "frontend"
    Push-Location $front
    try {
        Write-Step "Instalando dependências do frontend"
        & npm install
        Write-Step "Compilando frontend (vite build)"
        & npm run build
        Write-Ok "Frontend compilado em frontend\dist"
    } finally { Pop-Location }
}

function Register-Services([string]$nssmExe) {
    if ($SkipServices) { Write-Warn "Registro de serviços ignorado (-SkipServices)"; return }

    $svcApi   = "EnvioApolices-API"
    $svcFront = "EnvioApolices-Front"
    $backend  = Join-Path $InstallDir "backend"
    $frontend = Join-Path $InstallDir "frontend"
    $py       = Join-Path $backend ".venv\Scripts\python.exe"
    $run      = Join-Path $backend "run.py"

    # Remove serviços antigos (se existirem)
    foreach ($s in @($svcApi, $svcFront)) {
        & $nssmExe stop $s 2>$null | Out-Null
        & $nssmExe remove $s confirm 2>$null | Out-Null
    }

    Write-Step "Registrando serviço $svcApi"
    & $nssmExe install $svcApi $py $run
    & $nssmExe set $svcApi AppDirectory $backend
    & $nssmExe set $svcApi DisplayName "Envio Apolices - API (FastAPI)"
    & $nssmExe set $svcApi Description "Backend FastAPI do Sistema de Envio de Apolices"
    & $nssmExe set $svcApi Start SERVICE_AUTO_START
    & $nssmExe set $svcApi AppStdout (Join-Path $backend "logs\api.out.log")
    & $nssmExe set $svcApi AppStderr (Join-Path $backend "logs\api.err.log")
    New-Item -ItemType Directory -Path (Join-Path $backend "logs") -Force | Out-Null

    Write-Step "Iniciando $svcApi"
    & $nssmExe start $svcApi

    if (-not $SkipFrontend) {
        $npx = (Get-Command npx -ErrorAction SilentlyContinue).Source
        if ($npx) {
            Write-Step "Registrando serviço $svcFront (npx vite preview)"
            & $nssmExe install $svcFront $npx "vite preview --host 0.0.0.0 --port $FrontPort"
            & $nssmExe set $svcFront AppDirectory $frontend
            & $nssmExe set $svcFront DisplayName "Envio Apolices - Frontend (Vite preview)"
            & $nssmExe set $svcFront Start SERVICE_AUTO_START
            & $nssmExe set $svcFront AppStdout (Join-Path $frontend "front.out.log")
            & $nssmExe set $svcFront AppStderr (Join-Path $frontend "front.err.log")
            & $nssmExe start $svcFront
        } else {
            Write-Warn "npx não encontrado; serviço de frontend não foi registrado."
        }
    }

    Write-Ok "Serviços registrados"
}

function Open-Firewall {
    Write-Step "Liberando portas $ServicePort e $FrontPort no firewall"
    try {
        New-NetFirewallRule -DisplayName "EnvioApolices-API"   -Direction Inbound -Protocol TCP -LocalPort $ServicePort -Action Allow -ErrorAction SilentlyContinue | Out-Null
        New-NetFirewallRule -DisplayName "EnvioApolices-Front" -Direction Inbound -Protocol TCP -LocalPort $FrontPort   -Action Allow -ErrorAction SilentlyContinue | Out-Null
        Write-Ok "Regras de firewall criadas"
    } catch {
        Write-Warn "Falha ao criar regras de firewall: $_"
    }
}

# ============== MAIN ==============
Assert-Admin
Write-Step "Instalando em $InstallDir"

Install-Python
Install-Node
$nssm = Install-NSSM

Deploy-Sources
Setup-BackendEnv
Build-Frontend
Open-Firewall
Register-Services $nssm

Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Ok  "Instalação concluída."
Write-Host "  Backend API:  http://<ip-do-servidor>:$ServicePort/docs" -ForegroundColor White
Write-Host "  Frontend:     http://<ip-do-servidor>:$FrontPort"        -ForegroundColor White
Write-Host "  Serviços:     Get-Service EnvioApolices-*"               -ForegroundColor White
Write-Host "  Config:       $InstallDir\backend\.env"                  -ForegroundColor White
Write-Host "========================================================" -ForegroundColor Green
