"""CRUD de usuários (só admin)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..auth import require_admin, hash_senha


router = APIRouter(prefix="/api/usuarios", tags=["usuarios"])


@router.get("", response_model=list[schemas.UsuarioOut])
def listar(db: Session = Depends(get_db), _=Depends(require_admin)):
    return db.query(models.Usuario).order_by(models.Usuario.username).all()


@router.post("", response_model=schemas.UsuarioOut, status_code=201)
def criar(payload: schemas.UsuarioCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    if db.query(models.Usuario).filter(models.Usuario.username == payload.username).first():
        raise HTTPException(400, "Username já existe")

    u = models.Usuario(
        username=payload.username,
        nome=payload.nome,
        email=payload.email,
        senha_hash=hash_senha(payload.senha),
        is_admin=payload.is_admin,
        ativo=payload.ativo,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@router.put("/{user_id}", response_model=schemas.UsuarioOut)
def atualizar(
    user_id: int,
    payload: schemas.UsuarioUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    u = db.get(models.Usuario, user_id)
    if not u:
        raise HTTPException(404, "Usuário não encontrado")

    data = payload.model_dump(exclude_unset=True)
    if "senha" in data and data["senha"]:
        u.senha_hash = hash_senha(data.pop("senha"))
    else:
        data.pop("senha", None)

    for k, v in data.items():
        setattr(u, k, v)

    db.commit()
    db.refresh(u)
    return u


@router.delete("/{user_id}", status_code=204)
def remover(user_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    u = db.get(models.Usuario, user_id)
    if not u:
        raise HTTPException(404, "Usuário não encontrado")
    db.delete(u)
    db.commit()
