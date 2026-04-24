"""Orquestra o ciclo completo de um envio (AVULSO ou FULL).

Passos:
1. Opcionalmente junta capa (PDF em capas/) + apólice num só ficheiro
2. Copiar PDF (final) para backup
3. Enviar e-mail com o PDF anexado
4. Registrar na tabela de envios com status final
"""
from __future__ import annotations

import logging
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from .. import models
from ..config import settings
from . import email_service, backup_service, pdf_service


def _frases_dashboard_email(db: Session) -> str | None:
    rc = db.get(models.RuntimeConfig, 1)
    if not rc or not rc.email_frases_dashboard:
        return None
    t = rc.email_frases_dashboard.strip()
    return t or None

log = logging.getLogger(__name__)


def _resolver_caminho_capa() -> Path | None:
    if not settings.capa_enabled:
        return None
    capa = settings.data_path(settings.capa_folder) / settings.capa_arquivo_padrao
    if capa.is_file():
        log.info("Capa a usar: %s", capa)
        return capa
    log.info("Capa não aplicada (ficheiro inexistente): %s", capa)
    return None


def _preparar_pdf_final(original: Path) -> tuple[Path, str, Path | None]:
    """(ficheiro a usar no backup/email, nome_arquivo_final, temp a apagar ou None)."""
    capa = _resolver_caminho_capa()
    if not capa:
        return original, original.name, None
    tmp = Path(tempfile.gettempdir()) / f"envio_mesclado_{uuid.uuid4().hex}.pdf"
    try:
        pdf_service.mesclar_capa_e_apolice(capa, original, tmp)
        nome = f"com_capa_{original.name}"
        log.info("PDF mesclado com capa: %s + %s -> %s", capa.name, original.name, nome)
        return tmp, nome, tmp
    except Exception as e:
        log.exception("Junção com capa falhou; usa PDF original. Erro: %s", e)
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        return original, original.name, None


def processar_envio(
    db: Session,
    *,
    cliente: models.Cliente,
    caminho_pdf: str | Path,
    tipo_envio: str,
    numero_apolice: str | None = None,
    assunto_customizado: str | None = None,
    mensagem_customizada: str | None = None,
    nome_arquivo_original: str | None = None,
) -> models.Envio:
    caminho_pdf = Path(caminho_pdf)
    pdf_final, nome_final, temp_mesclado = _preparar_pdf_final(caminho_pdf)
    frases_dashboard = _frases_dashboard_email(db)

    # Regra do painel: FULL e AVULSO só podem ocorrer com frases definidas.
    if not frases_dashboard:
        raise ValueError(
            "Defina as frases no Dashboard para permitir envios."
        )

    envio = models.Envio(
        cliente_id=cliente.id,
        tipo_envio=tipo_envio,
        nome_arquivo_original=nome_arquivo_original or caminho_pdf.name,
        nome_arquivo_final=nome_final,
        numero_apolice=numero_apolice,
        status="pendente",
    )
    db.add(envio)
    db.commit()
    db.refresh(envio)

    try:
        # 1) backup (PDF já com capa quando configurado)
        destino = backup_service.copiar_para_backup(
            pdf_final, cliente.nome, nome_arquivo_destino=nome_final
        )
        envio.caminho_backup = str(destino)

        # 2) e-mail
        assunto = assunto_customizado or email_service.formatar_assunto(numero_apolice)
        corpo = email_service.renderizar_template(
            cliente_nome=cliente.nome,
            numero_apolice=numero_apolice,
            mensagem=None,
            frases_dashboard=frases_dashboard,
        )
        email_service.enviar_email(
            destinatario=cliente.email,
            assunto=assunto,
            corpo_html=corpo,
            anexos=[pdf_final],
            nome_anexo_pdf=nome_final if temp_mesclado is not None else None,
        )

        envio.assunto_email = assunto
        envio.status = "enviado"
        envio.enviado_em = datetime.utcnow()
    except Exception as exc:
        envio.status = "erro"
        envio.erro_msg = str(exc)[:2000]
    finally:
        if temp_mesclado is not None:
            temp_mesclado.unlink(missing_ok=True)
        db.commit()
        db.refresh(envio)

    return envio
