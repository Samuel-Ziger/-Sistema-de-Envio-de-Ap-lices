"""Status geral do sistema."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..config import settings
from .. import models, schemas


router = APIRouter(prefix="/api", tags=["status"])


@router.get("/status", response_model=schemas.StatusOut)
def status(db: Session = Depends(get_db)):
    return schemas.StatusOut(
        status="ok",
        versao="1.0.0",
        auth_enabled=settings.auth_enabled,
        full_enabled=settings.full_enabled,
        full_watch_folder=settings.full_watch_folder,
        total_clientes=db.query(models.Cliente).count(),
        total_envios=db.query(models.Envio).count(),
    )


@router.get("/health")
def health():
    return {"ok": True}
