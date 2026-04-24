# Inicializadores — como usar

Esta pasta reúne **atalhos em batch** para arrancar ou parar o sistema no Windows. O conteúdo está dividido em **dois cenários**; escolha a pasta certa para a sua máquina.

## Qual pasta devo usar?

| Situação | Abra esta pasta e siga o README |
|----------|-----------------------------------|
| **PC normal** (Windows 10/11), desenvolvimento ou operador **sem** serviços Windows instalados | [`maquina-local/`](maquina-local/README.md) |
| **Windows Server** (ou PC) **já instalado** com `installer\install.ps1` — serviços `EnvioApolices-*` | [`windows-server/`](windows-server/README.md) |

## Resumo rápido

- **Máquina local:** duplo clique em `Instalar-Primeira-Vez.bat` (uma vez), depois `Iniciar-Sistema.bat` sempre que quiser trabalhar. Aparecem **duas janelas pretas** (API + painel); feche-as para desligar tudo.
- **Servidor:** depois do instalador, use `Iniciar-Servicos-Windows.bat` e `Parar-Servicos-Windows.bat` **como administrador**, ou os comandos PowerShell descritos no README do servidor.

## Onde está o código

Os `.bat` assumem que a **raiz do projeto** é a pasta `envio-sistema` (onde estão `backend\` e `frontend\`). Não mova só os `.bat` para outro sítio sem copiar o projeto inteiro.

Documentação geral do projeto: [`../README.md`](../README.md).
