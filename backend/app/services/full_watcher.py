"""Modo FULL: varre pasta de entrada, processa PDFs, envia e-mail.

Roda em uma thread separada iniciada no lifespan do FastAPI.
Usa polling simples (mais confiável que watchdog em mounts de rede Windows).
"""
from __future__ import annotations

import logging
import threading
import time
from datetime import datetime, date
from pathlib import Path

from sqlalchemy.orm import Session

from ..config import settings
from ..database import SessionLocal
from .. import models
from . import envio_service, pdf_service


log = logging.getLogger("full_watcher")


class FullWatcher:
    def __init__(self) -> None:
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._last_daily_scan_date: date | None = None

    def start(self) -> None:
        if not settings.full_enabled:
            log.info("Modo FULL desativado (.env FULL_ENABLED=false)")
            return
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="full-watcher")
        self._thread.start()
        log.info(
            "Modo FULL iniciado - pasta=%s (intervalo e ON/OFF pelo painel / tabela runtime_config)",
            settings.data_path(settings.full_watch_folder),
        )

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)

    # -------------- loop --------------
    def _run(self) -> None:
        pasta = settings.data_path(settings.full_watch_folder)
        pasta.mkdir(parents=True, exist_ok=True)
        while not self._stop.is_set():
            db: Session = SessionLocal()
            try:
                rc = db.get(models.RuntimeConfig, 1)
                scan_active = rc.full_scan_active if rc else True
                interval = (
                    rc.full_scan_interval_seconds
                    if rc
                    else settings.full_scan_interval_seconds
                )
                exec_time = rc.full_scan_exec_time if rc else "08:00"
            finally:
                db.close()

            interval = max(10, min(3600, int(interval)))

            if scan_active:
                try:
                    if self._deve_executar_agora(exec_time):
                        self._scan(pasta)
                except Exception as e:
                    log.exception("Erro no watcher FULL: %s", e)
            else:
                log.debug("FULL pausado pelo painel (interruptor desligado)")

            self._stop.wait(interval)

    def _deve_executar_agora(self, exec_time: str | None) -> bool:
        """Executa uma vez por dia no horário HH:MM definido.

        Se o horário estiver inválido/vazio, mantém comportamento antigo (scan por intervalo).
        """
        if not exec_time:
            return True
        try:
            hora = int(exec_time[0:2])
            minuto = int(exec_time[3:5])
            if exec_time[2] != ":":
                return True
        except Exception:
            return True

        agora = datetime.now()
        hoje = agora.date()
        momento_programado = agora.replace(hour=hora, minute=minuto, second=0, microsecond=0)
        if agora >= momento_programado and self._last_daily_scan_date != hoje:
            self._last_daily_scan_date = hoje
            return True
        return False

    def _scan(self, pasta: Path) -> None:
        pdfs = sorted(p for p in pasta.glob("*.pdf") if p.is_file())
        if not pdfs:
            return

        log.info("FULL: %d PDF(s) encontrados em %s", len(pdfs), pasta)
        db: Session = SessionLocal()
        try:
            for pdf in pdfs:
                self._processar_um(db, pdf)
        finally:
            db.close()

    def _processar_um(self, db: Session, pdf: Path) -> None:
        try:
            dados = pdf_service.extrair_dados(pdf)
        except Exception as e:
            log.error("FULL: falha extraindo %s: %s", pdf.name, e)
            return

        cliente = self._achar_cliente(db, dados)
        if not cliente:
            log.warning(
                "FULL: cliente não identificado para %s (cpf=%s cnpj=%s). "
                "Arquivo permanece na pasta para análise manual.",
                pdf.name, dados.cpf, dados.cnpj,
            )
            return

        try:
            envio = envio_service.processar_envio(
                db,
                cliente=cliente,
                caminho_pdf=pdf,
                tipo_envio="FULL",
                numero_apolice=dados.numero_apolice,
                nome_arquivo_original=pdf.name,
            )
        except ValueError as e:
            log.warning("FULL: %s", e)
            return

        # Move PDF para processados (sucesso) ou mantém (erro) para retentativa manual
        if envio.status == "enviado":
            destino = settings.data_path(settings.processed_folder)
            destino.mkdir(parents=True, exist_ok=True)
            try:
                pdf.rename(destino / pdf.name)
            except Exception as e:
                log.error("FULL: não foi possível mover %s: %s", pdf.name, e)
        else:
            log.error("FULL: envio com erro para %s: %s", pdf.name, envio.erro_msg)

    def _achar_cliente(self, db: Session, dados: pdf_service.DadosPDF) -> models.Cliente | None:
        if dados.cpf:
            c = db.query(models.Cliente).filter(models.Cliente.cpf == dados.cpf).first()
            if c:
                return c
        if dados.cnpj:
            c = db.query(models.Cliente).filter(models.Cliente.cnpj == dados.cnpj).first()
            if c:
                return c
        return None


watcher_global = FullWatcher()
