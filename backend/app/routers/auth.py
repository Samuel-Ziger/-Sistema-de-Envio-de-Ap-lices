"""Rotas de autenticação."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..config import settings
from .. import models, schemas
from ..auth import verificar_senha, criar_token
from ..services.data_crypto_service import (
    backend_access_enabled,
    encryption_enabled,
    verify_backend_access,
)


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=schemas.TokenOut)
def login(payload: schemas.LoginPayload, db: Session = Depends(get_db)):
    user = (
        db.query(models.Usuario)
        .filter(models.Usuario.username == payload.username)
        .first()
    )
    if not user or not user.ativo or not verificar_senha(payload.senha, user.senha_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token = criar_token(user.username, {"is_admin": user.is_admin})
    return schemas.TokenOut(access_token=token, user=user)


@router.get("/status")
def auth_status():
    return {
        "auth_enabled": settings.auth_enabled,
        "backend_access_enabled": backend_access_enabled(),
        "data_encryption_enabled": encryption_enabled(),
    }


@router.post("/verificar-acesso-backend")
def verificar_acesso_backend(payload: schemas.BackendAccessVerifyIn):
    """Valida a chave de acesso (rota pública para o painel testar antes de guardar)."""
    if not backend_access_enabled():
        return {"ok": True, "mensagem": "Porta de acesso desativada no servidor."}
    if verify_backend_access(payload.chave):
        return {"ok": True}
    raise HTTPException(status_code=403, detail="Chave de acesso inválida")
