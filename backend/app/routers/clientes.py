"""CRUD de clientes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..auth import require_user


router = APIRouter(prefix="/api/clientes", tags=["clientes"])


@router.get("", response_model=list[schemas.ClienteOut])
def listar(
    q: str | None = Query(None, description="Busca em nome, email, cpf, cnpj"),
    ativo: bool | None = None,
    db: Session = Depends(get_db),
    _=Depends(require_user),
):
    query = db.query(models.Cliente)
    if q:
        ilike = f"%{q}%"
        query = query.filter(
            or_(
                models.Cliente.nome.ilike(ilike),
                models.Cliente.email.ilike(ilike),
                models.Cliente.cpf.ilike(ilike),
                models.Cliente.cnpj.ilike(ilike),
            )
        )
    if ativo is not None:
        query = query.filter(models.Cliente.ativo == ativo)

    return query.order_by(models.Cliente.nome).all()


@router.get("/{cid}", response_model=schemas.ClienteOut)
def obter(cid: int, db: Session = Depends(get_db), _=Depends(require_user)):
    c = db.get(models.Cliente, cid)
    if not c:
        raise HTTPException(404, "Cliente não encontrado")
    return c


@router.post("", response_model=schemas.ClienteOut, status_code=201)
def criar(
    payload: schemas.ClienteCreate,
    db: Session = Depends(get_db),
    _=Depends(require_user),
):
    c = models.Cliente(**payload.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.put("/{cid}", response_model=schemas.ClienteOut)
def atualizar(
    cid: int,
    payload: schemas.ClienteUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_user),
):
    c = db.get(models.Cliente, cid)
    if not c:
        raise HTTPException(404, "Cliente não encontrado")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return c


@router.delete("/{cid}", status_code=204)
def remover(cid: int, db: Session = Depends(get_db), _=Depends(require_user)):
    c = db.get(models.Cliente, cid)
    if not c:
        raise HTTPException(404, "Cliente não encontrado")
    db.delete(c)
    db.commit()
