"""Envio avulso (upload manual + e-mail imediato) e histórico."""
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
        q = q.filter(models.Envio.tipo_envio == tipo.upper())
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


@router.post("/avulso", response_model=schemas.EnvioOut, status_code=201)
async def envio_avulso(
    arquivo: UploadFile = File(..., description="PDF da apólice"),
    cliente_id: int | None = Form(None),
    cliente_novo: str | None = Form(
        None, description="JSON com os campos de ClienteCreate"
    ),
    numero_apolice: str | None = Form(None),
    assunto: str | None = Form(None),
    mensagem: str | None = Form(None),
    extrair_dados: bool = Form(
        False, description="Se true, tenta extrair apólice/CPF/CNPJ do PDF"
    ),
    db: Session = Depends(get_db),
    _=Depends(require_user),
):
    # 1. Resolver cliente
    cliente: models.Cliente | None = None
    if cliente_id:
        cliente = db.get(models.Cliente, cliente_id)
        if not cliente:
            raise HTTPException(404, "Cliente informado não existe")
    elif cliente_novo:
        try:
            dados = schemas.ClienteCreate(**json.loads(cliente_novo))
        except Exception as e:
            raise HTTPException(400, f"cliente_novo inválido: {e}")
        cliente = models.Cliente(**dados.model_dump())
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
    else:
        raise HTTPException(400, "Informe cliente_id OU cliente_novo")

    # 2. Salvar upload em pasta temporária
    up = settings.data_path(settings.upload_folder)
    up.mkdir(parents=True, exist_ok=True)
    nome_seguro = f"{uuid.uuid4().hex}_{arquivo.filename or 'anexo.pdf'}"
    destino_up = up / nome_seguro
    with destino_up.open("wb") as fh:
        fh.write(await arquivo.read())

    # 3. Opcional: extrair dados do PDF
    if extrair_dados:
        try:
            dados_pdf = pdf_service.extrair_dados(destino_up)
            if not numero_apolice and dados_pdf.numero_apolice:
                numero_apolice = dados_pdf.numero_apolice
        except Exception:
            pass  # não interrompe o envio

    # 4. Processar envio
    envio = envio_service.processar_envio(
        db,
        cliente=cliente,
        caminho_pdf=destino_up,
        tipo_envio="AVULSO",
        numero_apolice=numero_apolice,
        assunto_customizado=assunto,
        mensagem_customizada=mensagem,
        nome_arquivo_original=arquivo.filename,
    )

    # 5. Move arquivo original p/ processados
    try:
        proc = settings.data_path(settings.processed_folder)
        proc.mkdir(parents=True, exist_ok=True)
        destino_up.rename(proc / nome_seguro)
    except Exception:
        pass

    return envio
