# Instalador — Windows Server

## Pré-requisitos
- Windows Server 2019 / 2022
- Acesso como **Administrador**
- Conexão com a internet (para baixar Python, Node e NSSM)

## Instalação

Abra o **PowerShell como Administrador** na pasta `installer/` e rode:

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
.\install.ps1
```

Opcionais:

```powershell
.\install.ps1 -InstallDir "D:\apps\envio" -ServicePort 8000 -FrontPort 5173
.\install.ps1 -SkipFrontend        # só o backend
.\install.ps1 -SkipServices        # não registra serviços, só prepara
```

O script faz automaticamente:
1. Instala Python 3.11+ (via winget ou download direto)
2. Instala Node.js LTS
3. Baixa e instala **NSSM** em `C:\tools\nssm\` e adiciona ao PATH
4. Copia os fontes para `C:\envio-sistema\`
5. Cria o venv Python, instala `requirements.txt`
6. Faz `npm install` + `npm run build` no frontend
7. Registra os serviços Windows `EnvioApolices-API` e `EnvioApolices-Front`
8. Libera as portas no firewall

## Atalhos no servidor (iniciar / parar serviços)

Na máquina onde correu o instalador, use a pasta copiada para o destino, por exemplo:

`C:\envio-sistema\inicializadores\windows-server\`

- **`Iniciar-Servicos-Windows.bat`** — inicia API e front (executar **como Administrador**).
- **`Parar-Servicos-Windows.bat`** — para os serviços.

Resumo: ver **`inicializadores\windows-server\README.md`** no repositório (o mesmo ficheiro é copiado para `InstallDir`).

## Após instalar

Edite o arquivo de configuração do backend:
```
C:\envio-sistema\backend\.env
```
Ajuste principalmente:
- `SMTP_*` (credenciais do e-mail)
- `FULL_WATCH_FOLDER` (pasta que o watcher vai varrer)
- `ADMIN_PASSWORD` (senha inicial do admin)

Reinicie o serviço:
```powershell
Restart-Service EnvioApolices-API
```

Ver status:
```powershell
Get-Service EnvioApolices-*
```

## Usar o front em outra máquina da rede

1. Copie a pasta `frontend/` para a máquina cliente
2. Edite `frontend/.env`:
   ```
   VITE_API_URL=http://IP-DO-SERVIDOR:8000
   ```
3. `npm install && npm run dev` (ou `npm run build && npm run preview`)

## Desinstalação

```powershell
.\uninstall.ps1                 # remove tudo
.\uninstall.ps1 -KeepData       # remove serviços, mantém arquivos/backup
```
