"""Envio MANUAL (upload manual + e-mail imediato), demonstração e histórico."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from .. import models, schemas
from ..auth import require_user
from ..services import envio_service, pdf_service


router = APIRouter(prefix="/api/envios", tags=["envios"])


@router.get("", response_model=list[schemas.EnvioOut])
def listar(
    cliente_id: int | None = None,
    status: str | None = None,
    tipo: str | None = None,
    tipo_codigo: str | None = None,
    dias: int | None = Query(None, description="Filtrar envios dos últimos N dias"),
    db: Session = Depends(get_db),
    _=Depends(require_user),
):
    q = db.query(models.Envio)
    if cliente_id:
        q = q.filter(models.Envio.cliente_id == cliente_id)
    if status:
        q = q.filter(models.Envio.status == status)
    if tipo:
        # aceita FULL, MANUAL e o legado AVULSO (sinônimo de MANUAL)
        t = tipo.upper()
        if t == "AVULSO":
            t = "MANUAL"
        q = q.filter(models.Envio.tipo_envio == t)
    if tipo_codigo:
        q = q.filter(models.Envio.tipo_codigo == tipo_codigo)
    if dias:
        limite = datetime.utcnow() - timedelta(days=dias)
        q = q.filter(models.Envio.criado_em >= limite)

    return q.order_by(models.Envio.criado_em.desc()).limit(500).all()


@router.get("/{eid}", response_model=schemas.EnvioOut)
def obter(eid: int, db: Session = Depends(get_db), _=Depends(require_user)):
    e = db.get(models.Envio, eid)
    if not e:
        raise HTTPException(404, "Envio não encontrado")
    return e


def _resolver_cliente(
    db: Session, cliente_id: int | None, cliente_novo_json: str | None
) -> models.Cliente:
    if cliente_id:
        cli = db.get(models.Cliente, cliente_id)
        if not cli:
            raise HTTPException(404, "Cliente informado não existe")
        return cli
    if cliente_novo_json:
        try:
            dados = schemas.ClienteCreate(**json.loads(cliente_novo_json))
        except Exception as e:
            raise HTTPException(400, f"cliente_novo inválido: {e}")
        cli = models.Cliente(**dados.model_dump())
        db.add(cli)
        db.commit()
        db.refresh(cli)
        return cli
    raise HTTPException(400, "Informe cliente_id OU cliente_novo")


async def _processar_request_manual(
    *,
    db: Session,
    arquivo: UploadFile,
    boleto: UploadFile | None,
    cliente_id: int | None,
    cliente_novo: str | None,
    numero_apolice: str | None,
    assunto: str | None,
    extrair_dados: bool,
    tipo_codigo: str | None,
    auto_id: int | None,
    corpo_email_id: int | None,
    assinatura_id: int | None,
):
    cliente = _resolver_cliente(db, cliente_id, cliente_novo)

    up = settings.data_path(settings.upload_folder)
    up.mkdir(parents=True, exist_ok=True)
    nome_seguro = f"{uuid.uuid4().hex}_{arquivo.filename or 'anexo.pdf'}"
    destino_up = up / nome_seguro
    with destino_up.open("wb") as fh:
        fh.write(await arquivo.read())

    if extrair_dados:
        try:
            dados_pdf = pdf_service.extrair_dados(destino_up)
            if not numero_apolice and dados_pdf.numero_apolice:
                numero_apolice = dados_pdf.numero_apolice
        except Exception:
            pass

    auto: models.Auto | None = None
    if auto_id:
        auto = db.get(models.Auto, auto_id)
        if auto and auto.cliente_id != cliente.id:
            auto = None

    try:
        envio = envio_service.processar_envio(
            db,
            cliente=cliente,
            caminho_pdf=destino_up,
            tipo_envio="MANUAL",
            tipo_codigo=tipo_codigo,
            auto=auto,
            numero_apolice=numero_apolice,
            assunto_customizado=assunto,
            corpo_email_id=corpo_email_id,
            assinatura_id=assinatura_id,
            nome_arquivo_original=arquivo.filename,
        )
    except ValueError as e:
        raise HTTPException(400, str(e))

    try:
        proc = settings.data_path(settings.processed_folder)
        proc.mkdir(parents=True, exist_ok=True)
        destino_up.rename(proc / nome_seguro)
    except Exception:
        pass

    return envio


@router.post("/manual", response_model=schemas.EnvioOut, status_code=201)
async def envio_manual(
    arquivo: UploadFile = File(..., description="PDF da apólice"),
    boleto: UploadFile | None = File(None, description="PDF de boleto opcional"),
    cliente_id: int | None = Form(None),
    cliente_novo: str | None = Form(None),
    numero_apolice: str | None = Form(None),
    assunto: str | None = Form(None),
    extrair_dados: bool = Form(True),
    tipo_codigo: str | None = Form(None),
    auto_id: int | None = Form(None),
    corpo_email_id: int | None = Form(None),
    assinatura_id: int | None = Form(None),
    db: Session = Depends(get_db),
    _=Depends(require_user),
):
    return await _processar_request_manual(
        db=db,
        arquivo=arquivo,
        boleto=boleto,
        cliente_id=cliente_id,
        cliente_novo=cliente_novo,
        numero_apolice=numero_apolice,
        assunto=assunto,
        extrair_dados=extrair_dados,
        tipo_codigo=tipo_codigo,
        auto_id=auto_id,
        corpo_email_id=corpo_email_id,
        assinatura_id=assinatura_id,
    )


@router.post("/avulso", response_model=schemas.EnvioOut, status_code=201)
async def envio_avulso_legado(
    arquivo: UploadFile = File(...),
    cliente_id: int | None = Form(None),
    cliente_novo: str | None = Form(None),
    numero_apolice: str | None = Form(None),
    assunto: str | None = Form(None),
    mensagem: str | None = Form(None),
    extrair_dados: bool = Form(False),
    tipo_codigo: str | None = Form(None),
    auto_id: int | None = Form(None),
    corpo_email_id: int | None = Form(None),
    assinatura_id: int | None = Form(None),
    db: Session = Depends(get_db),
    _=Depends(require_user),
):
    """Alias legado da rota /manual — mantido para compat com clientes antigos."""
    return await _processar_request_manual(
        db=db,
        arquivo=arquivo,
        boleto=None,
        cliente_id=cliente_id,
        cliente_novo=cliente_novo,
        numero_apolice=numero_apolice,
        assunto=assunto,
        extrair_dados=extrair_dados,
        tipo_codigo=tipo_codigo,
        auto_id=auto_id,
        corpo_email_id=corpo_email_id,
        assinatura_id=assinatura_id,
    )


@router.post("/demonstrar", response_model=schemas.EnvioDemoOut)
async def demonstrar_email(
    arquivo: UploadFile | None = File(None),
    cliente_id: int | None = Form(None),
    cliente_novo: str | None = Form(None),
    numero_apolice: str | None = Form(None),
    extrair_dados: bool = Form(True),
    tipo_codigo: str | None = Form(None),
    auto_id: int | None = Form(None),
    corpo_email_id: int | None = Form(None),
    assinatura_id: int | None = Form(None),
    db: Session = Depends(get_db),
    _=Depends(require_user),
):
    """Não envia: só renderiza assunto/corpo do e-mail com os dados informados."""
    cliente = _resolver_cliente(db, cliente_id, cliente_novo)

    if arquivo and arquivo.filename and extrair_dados:
        up = settings.data_path(settings.upload_folder)
        up.mkdir(parents=True, exist_ok=True)
        tmp = up / f"demo_{uuid.uuid4().hex}_{arquivo.filename}"
        try:
            tmp.write_bytes(await arquivo.read())
            try:
                d = pdf_service.extrair_dados(tmp)
                if not numero_apolice and d.numero_apolice:
                    numero_apolice = d.numero_apolice
            except Exception:
                pass
        finally:
            try:
                tmp.unlink()
            except Exception:
                pass

    auto: models.Auto | None = None
    if auto_id:
        auto = db.get(models.Auto, auto_id)
        if auto and auto.cliente_id != cliente.id:
            auto = None

    out = envio_service.renderizar_demonstracao(
        db,
        cliente=cliente,
        auto=auto,
        numero_apolice=numero_apolice,
        tipo_envio="MANUAL",
        tipo_codigo=tipo_codigo,
        assinatura_id=assinatura_id,
        corpo_email_id=corpo_email_id,
    )
    return out
