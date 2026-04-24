"""Orquestra o ciclo completo de um envio (AVULSO ou FULL).

Passos:
1. Resolver cliente (já existe? criar?)
2. Copiar PDF para backup
3. Enviar e-mail com o PDF anexado
4. Registrar na tabela de envios com status final
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from .. import models
from . import email_service, backup_service


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

    envio = models.Envio(
        cliente_id=cliente.id,
        tipo_envio=tipo_envio,
        nome_arquivo_original=nome_arquivo_original or caminho_pdf.name,
        nome_arquivo_final=caminho_pdf.name,
        numero_apolice=numero_apolice,
        status="pendente",
    )
    db.add(envio)
    db.commit()
    db.refresh(envio)

    try:
        # 1) backup
        destino = backup_service.copiar_para_backup(caminho_pdf, cliente.nome)
        envio.caminho_backup = str(destino)

        # 2) e-mail
        assunto = assunto_customizado or email_service.formatar_assunto(numero_apolice)
        corpo = email_service.renderizar_template(
            cliente_nome=cliente.nome,
            numero_apolice=numero_apolice,
            mensagem=mensagem_customizada,
        )
        email_service.enviar_email(
            destinatario=cliente.email,
            assunto=assunto,
            corpo_html=corpo,
            anexos=[caminho_pdf],
        )

        envio.assunto_email = assunto
        envio.status = "enviado"
        envio.enviado_em = datetime.utcnow()
    except Exception as exc:
        envio.status = "erro"
        envio.erro_msg = str(exc)[:2000]
    finally:
        db.commit()
        db.refresh(envio)

    return envio
