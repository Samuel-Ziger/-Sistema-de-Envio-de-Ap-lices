# Máquina local — como usar

Esta pasta serve para **computadores normais** (Windows 10/11) ou para **desenvolvimento**: o backend e o frontend correm em **janelas de terminal** que você abre e fecha manualmente. **Não** usa os serviços Windows (`EnvioApolices-*`).

---

## Antes de começar (uma vez no PC)

1. Instale **[Python 3.11 ou superior](https://www.python.org/downloads/)** e marque a opção **“Add Python to PATH”**.
2. Instale **[Node.js LTS](https://nodejs.org/)** (inclui o `npm`).

Confirme no **cmd** ou PowerShell:

```text
python --version
npm --version
```

Se algum comando não for reconhecido, corrija o PATH antes de continuar.

---

## Passo a passo

### 1. Primeira vez — instalar dependências

1. Abra o Explorador de ficheiros e vá a esta pasta:  
   `envio-sistema\inicializadores\maquina-local\`
2. Faça **duplo clique** em **`Instalar-Primeira-Vez.bat`**.
3. Espere terminar (cria `backend\.venv`, instala pacotes Python, `npm install` no frontend, copia `.env` se não existir e tenta fazer o **build** do painel).

Se aparecer erro de permissão ou de rede, copie a mensagem e corrija (firewall, antivírus, etc.).

### 2. Dia a dia — subir API + painel

**Modo desenvolvimento** (recarrega o front ao editar código):

- Duplo clique em **`Iniciar-Sistema.bat`**.

**Modo “quase produção”** (painel já compilado, mais leve):

- Só funciona se existir `frontend\dist` (o passo 1 já tenta o `npm run build`).
- Duplo clique em **`Iniciar-Sistema-Preview.bat`**.

Vai abrir **duas janelas pretas**:

| Janela | O que é |
|--------|---------|
| **Envio de Apólices — API** | Backend FastAPI (porta **8000**) |
| **Envio de Apólices — Painel** | Vue / Vite (porta **5173**) |

O navegador deve abrir sozinho em **http://localhost:5173**.  
Para **parar**, feche as duas janelas (ou use `Ctrl+C` dentro de cada uma).

### 3. Configurar e-mail e pastas

Edite **`backend\.env`** na raiz do projeto (pasta `envio-sistema`). O mínimo para envio real de e-mail é preencher as variáveis **`SMTP_*`**. Reinicie a janela da API depois de alterar o `.env`.

---

## URLs úteis

| O quê | Endereço |
|-------|-----------|
| Painel | http://localhost:5173 |
| Documentação da API (Swagger) | http://localhost:8000/docs |

---

## Ficheiros desta pasta

| Ficheiro | Função |
|----------|--------|
| `Instalar-Primeira-Vez.bat` | Instalação inicial (venv, pip, npm, build opcional). |
| `Iniciar-Sistema.bat` | Sobe API + `npm run dev`. |
| `Iniciar-Sistema-Preview.bat` | Sobe API + `npm run preview` (precisa de `frontend\dist`). |
| `Gerar-Exe-Iniciador.bat` | Gera `dist-exe\IniciarEnvioApolices.exe` (opcional; ver secção abaixo). |
| `iniciar_tudo.py` | Mesma ideia que `Iniciar-Sistema.bat`, pela linha de comandos. |

### Linha de comandos (`iniciar_tudo.py`)

Na pasta **raiz** do repositório (`envio-sistema`):

```powershell
python inicializadores\maquina-local\iniciar_tudo.py
python inicializadores\maquina-local\iniciar_tudo.py --preview
python inicializadores\maquina-local\iniciar_tudo.py --no-browser
```

---

## Gerar o `.exe` (opcional)

1. Rode **`Gerar-Exe-Iniciador.bat`** (usa o Python de `backend\.venv` e instala o PyInstaller).
2. O ficheiro fica em **`inicializadores\maquina-local\dist-exe\IniciarEnvioApolices.exe`**.
3. Para distribuir: coloque o `.exe` na **raiz** do projeto, **ao lado** das pastas `backend\` e `frontend\`.  
   **Nota:** o cliente continua a precisar de **Python** e **Node** instalados; o `.exe` só automatiza os comandos.

---

## Problemas frequentes

| Problema | O que fazer |
|----------|-------------|
| “Python não está no PATH” | Reinstale o Python com “Add to PATH” ou adicione manualmente. |
| “Backend sem ambiente virtual” | Rode de novo `Instalar-Primeira-Vez.bat`. |
| “Falta frontend\dist” no preview | Na pasta `frontend`, execute `npm run build` ou rode a instalação primeira vez outra vez. |
| Porta 8000 ou 5173 ocupada | Feche outro programa que use a mesma porta ou altere portas no `.env` / Vite (avançado). |

---

## Servidor com serviços Windows

Se no futuro instalar com **`installer\install.ps1`** (NSSM), passe a usar os atalhos em **`inicializadores\windows-server\`** — ver o README dessa pasta.
