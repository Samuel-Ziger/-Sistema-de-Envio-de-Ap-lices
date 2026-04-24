"""Auth: JWT + hashing. Pode ser DESATIVADO via settings.auth_enabled.

Quando desativado, o endpoint /login continua funcionando para testes, mas as
dependencies `require_user` e `require_admin` deixam passar qualquer request
(retornando um "usuário anônimo" sintético). Assim todo o resto da API já
está preparado para ativar o login depois, apenas trocando AUTH_ENABLED=true
no .env.
"""
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from . import models


pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def hash_senha(senha: str) -> str:
    return pwd.hash(senha)


def verificar_senha(senha: str, hash_: str) -> bool:
    try:
        return pwd.verify(senha, hash_)
    except Exception:
        return False


def criar_token(subject: str, extra: dict | None = None) -> str:
    exp = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": subject, "exp": exp}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def _anon_user() -> models.Usuario:
    """Usuário sintético usado quando AUTH_ENABLED=false."""
    u = models.Usuario(
        id=0,
        username="anonimo",
        nome="Usuário Anônimo",
        email=None,
        senha_hash="",
        is_admin=True,
        ativo=True,
        created_at=datetime.utcnow(),
    )
    return u


def _decodar(token: str) -> dict:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {e}",
        )


def require_user(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str | None, Depends(oauth2)] = None,
) -> models.Usuario:
    if not settings.auth_enabled:
        return _anon_user()

    if not token:
        raise HTTPException(status_code=401, detail="Token ausente")

    data = _decodar(token)
    username = data.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Token sem subject")

    user = db.query(models.Usuario).filter(models.Usuario.username == username).first()
    if not user or not user.ativo:
        raise HTTPException(status_code=401, detail="Usuário inválido ou inativo")

    return user


def require_admin(user: Annotated[models.Usuario, Depends(require_user)]) -> models.Usuario:
    if not settings.auth_enabled:
        return user
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores")
    return user


def seed_admin(db: Session) -> None:
    """Garante que existe um admin inicial baseado no .env."""
    existe = (
        db.query(models.Usuario)
        .filter(models.Usuario.username == settings.admin_username)
        .first()
    )
    if existe:
        return

    admin = models.Usuario(
        username=settings.admin_username,
        nome="Administrador",
        email=None,
        senha_hash=hash_senha(settings.admin_password),
        is_admin=True,
        ativo=True,
    )
    db.add(admin)
    db.commit()
