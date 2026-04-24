"""Rotas de autenticação."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..config import settings
from .. import models, schemas
from ..auth import verificar_senha, criar_token


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
    return {"auth_enabled": settings.auth_enabled}
