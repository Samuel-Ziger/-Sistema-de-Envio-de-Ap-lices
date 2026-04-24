# Windows Server — como usar

Esta pasta é para máquinas em que o sistema foi instalado com **`installer\install.ps1`** (PowerShell **como administrador**). Nesse cenário o Windows regista os serviços:

- **`EnvioApolices-API`** — backend (FastAPI), porta típica **8000**
- **`EnvioApolices-Front`** — painel com `vite preview`, porta típica **5173**

O instalador copia o projeto para uma pasta de destino (por defeito **`C:\envio-sistema\`**). Os mesmos ficheiros desta pasta também são copiados para **`...\inicializadores\windows-server\`** nesse destino.

---

## Antes de usar estes atalhos

1. A instalação com **`installer\install.ps1`** tem de ter **corrido até ao fim** sem `-SkipServices` (a não ser que saiba que os serviços foram registados manualmente).
2. Confirme no PowerShell (como administrador):

```powershell
Get-Service EnvioApolices-*
```

Deve aparecer pelo menos **`EnvioApolices-API`**. O front pode faltar se na instalação não houve `npx` ou usou `-SkipFrontend`.

---

## Passo a passo — iniciar os serviços

1. Abra o Explorador e vá a:  
   `C:\envio-sistema\inicializadores\windows-server\`  
   (ou o seu `InstallDir` + `inicializadores\windows-server\`).
2. Clique com o botão direito em **`Iniciar-Servicos-Windows.bat`**.
3. Escolha **“Executar como administrador”** (é obrigatório: `net start` exige privilégios elevados).
4. Se a API falhar, leia a mensagem: o serviço pode não estar instalado (volte a correr o instalador).

**Parar** os serviços: mesmo processo com **`Parar-Servicos-Windows.bat`** (também como **administrador**).

---

## O que cada serviço faz

| Serviço | Conteúdo |
|---------|-----------|
| **EnvioApolices-API** | API REST, base de dados, envio de e-mail, **watcher FULL** e leitura de PDF — tudo no mesmo processo. |
| **EnvioApolices-Front** | Servir o painel já compilado (`vite preview`). |

Não existe um serviço separado “só para PDF”: o PDF é tratado **dentro da API**.

---

## Depois de mudar `backend\.env`

Sempre que alterar SMTP, pastas, etc., **reinicie a API**:

```powershell
Restart-Service EnvioApolices-API
```

(O front só precisa de reinício se mudar algo ligado ao build do painel.)

---

## Comandos PowerShell (alternativa ao .bat)

```powershell
# Iniciar
Start-Service EnvioApolices-API
Start-Service EnvioApolices-Front

# Ver estado
Get-Service EnvioApolices-*

# Parar
Stop-Service EnvioApolices-Front -ErrorAction SilentlyContinue
Stop-Service EnvioApolices-API   -ErrorAction SilentlyContinue
```

---

## URLs (no próprio servidor ou pela rede)

Substitua `localhost` pelo **IP ou nome** do servidor se aceder de outra máquina.

| O quê | Endereço típico |
|-------|------------------|
| Painel | http://localhost:5173 |
| API / Swagger | http://localhost:8000/docs |

Firewall: o instalador tenta criar regras para as portas configuradas (`-ServicePort`, `-FrontPort`).

---

## Ficheiros desta pasta

| Ficheiro | Função |
|----------|--------|
| `Iniciar-Servicos-Windows.bat` | `net start` da API e do front (admin). |
| `Parar-Servicos-Windows.bat` | `net stop` dos dois serviços (admin). |

---

## Documentação e PC sem serviços

- Instalação completa, firewall e desinstalação: **`installer\README-INSTALL.md`**.
- Para **não** usar serviços (PC de secretária, desenvolvimento): **`inicializadores\maquina-local\`** e o respetivo README.

---

## Problemas frequentes

| Problema | O que fazer |
|----------|-------------|
| “O serviço especificado não existe” | O NSSM não registou os serviços; execute `installer\install.ps1` de novo (como admin) ou use a pasta **maquina-local** se for só para testar no PC. |
| “Acesso negado” ao correr o .bat | Tem de ser **Executar como administrador**. |
| Front não inicia | Verifique se o serviço `EnvioApolices-Front` existe; na instalação pode ter sido omitido se faltava `npx` ou usou `-SkipFrontend`. A API pode funcionar sozinha; aceda ao Swagger em `:8000/docs`. |
| Alterou `.env` e nada mudou | `Restart-Service EnvioApolices-API`. |
