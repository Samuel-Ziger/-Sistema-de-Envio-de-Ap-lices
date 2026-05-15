"""Rotas de autenticação."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..config import settings
from .. import models, schemas
from ..auth import verificar_senha, criar_token, require_user, hash_senha
from ..services.data_crypto_service import (
    backend_access_enabled,
    encryption_enabled,
    verify_backend_access,
)
from ..services.password_policy import validate_password_strength


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

    token = criar_token(
        user.username,
        {
            "is_admin": user.is_admin,
            "must_change_password": user.must_change_password,
        },
    )
    return schemas.TokenOut(access_token=token, user=user)


@router.post("/trocar-senha", response_model=schemas.TrocaSenhaOut)
def trocar_senha(
    payload: schemas.TrocaSenhaIn,
    db: Session = Depends(get_db),
    user: models.Usuario = Depends(require_user),
):
    if payload.senha_nova != payload.senha_nova_confirmacao:
        raise HTTPException(400, "A nova senha e a confirmação não coincidem")

    if not verificar_senha(payload.senha_atual, user.senha_hash):
        raise HTTPException(400, "Senha atual incorreta")

    if verificar_senha(payload.senha_nova, user.senha_hash):
        raise HTTPException(400, "A nova senha deve ser diferente da atual")

    try:
        validate_password_strength(payload.senha_nova)
    except ValueError as e:
        raise HTTPException(400, str(e))

    user.senha_hash = hash_senha(payload.senha_nova)
    user.must_change_password = False
    db.commit()
    db.refresh(user)

    token = criar_token(
        user.username,
        {
            "is_admin": user.is_admin,
            "must_change_password": False,
        },
    )
    return schemas.TrocaSenhaOut(
        mensagem="Senha alterada com sucesso.",
        access_token=token,
        user=user,
    )


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
