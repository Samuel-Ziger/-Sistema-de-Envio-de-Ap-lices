#!/usr/bin/env python3
"""
Inicializador: sobe backend (FastAPI) e frontend (Vite dev ou preview).

Colocado em inicializadores/maquina-local/ — a raiz do repositório sobe dois níveis.

Uso (a partir da raiz do repo):
  python inicializadores\\maquina-local\\iniciar_tudo.py
  python inicializadores\\maquina-local\\iniciar_tudo.py --preview
  python inicializadores\\maquina-local\\iniciar_tudo.py --no-browser

Executável PyInstaller (gerado por Gerar-Exe-Iniciador.bat):
  Coloque IniciarEnvioApolices.exe na raiz do projeto, junto de backend\\ e frontend\\.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
import webbrowser

if getattr(sys, "frozen", False):
    ROOT = os.path.dirname(os.path.abspath(sys.executable))
else:
    _here = os.path.dirname(os.path.abspath(__file__))
    ROOT = os.path.normpath(os.path.join(_here, "..", ".."))

BACKEND = os.path.join(ROOT, "backend")
FRONTEND = os.path.join(ROOT, "frontend")
VENV_PY = os.path.join(BACKEND, ".venv", "Scripts", "python.exe")
NPM_CMD = "npm.cmd" if sys.platform == "win32" else "npm"


def _win_new_console_popen(args: list[str], cwd: str) -> subprocess.Popen:
    flags = 0
    if sys.platform == "win32":
        flags = subprocess.CREATE_NEW_CONSOLE
    return subprocess.Popen(args, cwd=cwd, creationflags=flags)


def main() -> int:
    parser = argparse.ArgumentParser(description="Sobe API + painel do sistema de envio.")
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Usa build estático (npm run preview); requer frontend/dist.",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Não abre o navegador automaticamente.",
    )
    args = parser.parse_args()

    if not os.path.isfile(VENV_PY):
        print(
            "Erro: não encontrado backend\\.venv. Rode Instalar-Primeira-Vez.bat "
            "(inicializadores\\maquina-local) primeiro."
        )
        return 1

    node_modules = os.path.join(FRONTEND, "node_modules")
    if not os.path.isdir(node_modules):
        print(
            "Erro: não encontrado frontend\\node_modules. Rode Instalar-Primeira-Vez.bat "
            "(inicializadores\\maquina-local) primeiro."
        )
        return 1

    if args.preview:
        dist_index = os.path.join(FRONTEND, "dist", "index.html")
        if not os.path.isfile(dist_index):
            print("Erro: falta frontend\\dist (rode npm run build no frontend).")
            return 1
        front_cmd = [NPM_CMD, "run", "preview"]
        delay = 5
    else:
        front_cmd = [NPM_CMD, "run", "dev"]
        delay = 6

    if sys.platform == "win32":
        api_line = (
            f'cd /d "{BACKEND}" && call .venv\\Scripts\\activate.bat && python run.py'
        )
        front_line = f'cd /d "{FRONTEND}" && {" ".join(front_cmd)}'
        _win_new_console_popen(
            [
                os.environ.get("COMSPEC", "cmd.exe"),
                "/k",
                api_line,
            ],
            cwd=ROOT,
        )
        time.sleep(2)
        _win_new_console_popen(
            [
                os.environ.get("COMSPEC", "cmd.exe"),
                "/k",
                front_line,
            ],
            cwd=ROOT,
        )
    else:
        subprocess.Popen([VENV_PY, "run.py"], cwd=BACKEND, start_new_session=True)
        time.sleep(2)
        subprocess.Popen(front_cmd, cwd=FRONTEND, start_new_session=True)

    if not args.no_browser:
        time.sleep(delay)
        webbrowser.open("http://localhost:5173/")

    print("Processos iniciados. Feche as janelas do terminal para encerrar API ou painel.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
