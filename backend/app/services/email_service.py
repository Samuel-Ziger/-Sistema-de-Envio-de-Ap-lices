"""Envio de e-mail via SMTP (síncrono, simples e robusto).

Usa smtplib padrão — sem dependência externa além de stdlib para o caso STARTTLS.
Anexa o PDF final e usa template Jinja2 opcional.
"""
from __future__ import annotations

import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path
from typing import Iterable

from jinja2 import Template

from ..config import settings


TEMPLATE_PADRAO = """
<html>
  <body style="font-family: Arial, sans-serif; color:#333;">
    <p>Prezado(a) <strong>{{ cliente_nome }}</strong>,</p>
    <p>Segue em anexo sua apólice{% if numero_apolice %} de número
       <strong>{{ numero_apolice }}</strong>{% endif %}.</p>
    {% if mensagem %}<p>{{ mensagem }}</p>{% endif %}
    <p>Em caso de dúvidas, responda este e-mail.</p>
    <p>Atenciosamente,<br/>{{ from_name }}</p>
  </body>
</html>
"""


def renderizar_template(
    *,
    cliente_nome: str,
    numero_apolice: str | None,
    mensagem: str | None,
    template_path: str | None = None,
) -> str:
    tpl = TEMPLATE_PADRAO
    if template_path:
        p = Path(template_path)
        if p.exists():
            tpl = p.read_text(encoding="utf-8")
    return Template(tpl).render(
        cliente_nome=cliente_nome,
        numero_apolice=numero_apolice,
        mensagem=mensagem,
        from_name=settings.smtp_from_name,
    )


def formatar_assunto(numero_apolice: str | None) -> str:
    tpl = settings.email_subject_default or "Envio de Apolice"
    try:
        return tpl.format(numero_apolice=numero_apolice or "")
    except Exception:
        return tpl


def enviar_email(
    *,
    destinatario: str,
    assunto: str,
    corpo_html: str,
    anexos: Iterable[str | Path] = (),
) -> None:
    if not settings.smtp_host:
        raise RuntimeError("SMTP não configurado (.env SMTP_HOST vazio)")

    msg = EmailMessage()
    msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    msg["To"] = destinatario
    msg["Subject"] = assunto
    msg.set_content("Sua apólice segue em anexo. (e-mail em HTML)")
    msg.add_alternative(corpo_html, subtype="html")

    for caminho in anexos:
        p = Path(caminho)
        if not p.exists():
            continue
        with p.open("rb") as fh:
            msg.add_attachment(
                fh.read(),
                maintype="application",
                subtype="pdf",
                filename=p.name,
            )

    contexto = ssl.create_default_context()
    if settings.smtp_use_tls:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30) as smtp:
            smtp.ehlo()
            smtp.starttls(context=contexto)
            smtp.ehlo()
            if settings.smtp_user:
                smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(msg)
    else:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30) as smtp:
            if settings.smtp_user:
                smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(msg)
