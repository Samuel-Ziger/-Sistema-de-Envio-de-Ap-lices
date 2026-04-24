"""Status geral do sistema e ajustes do modo FULL (painel)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..config import settings
from .. import models, schemas
from ..auth import require_user


router = APIRouter(prefix="/api", tags=["status"])


def _montar_status(db: Session) -> schemas.StatusOut:
    rc = db.get(models.RuntimeConfig, 1)
    env_on = settings.full_enabled
    scan_active = rc.full_scan_active if rc else True
    interval = (
        rc.full_scan_interval_seconds
        if rc
        else settings.full_scan_interval_seconds
    )
    interval = max(10, min(3600, int(interval)))
    effective = bool(env_on and scan_active)
    frases = ""
    if rc and rc.email_frases_dashboard:
        frases = rc.email_frases_dashboard.strip()
    exec_time = "08:00"
    if rc and rc.full_scan_exec_time:
        exec_time = rc.full_scan_exec_time
    return schemas.StatusOut(
        status="ok",
        versao="1.0.0",
        auth_enabled=settings.auth_enabled,
        full_enabled=effective,
        full_env_enabled=env_on,
        full_scan_active=scan_active,
        full_scan_interval_seconds=interval,
        full_scan_exec_time=exec_time,
        full_watch_folder=str(settings.data_path(settings.full_watch_folder)),
        email_frases_dashboard=frases,
        total_clientes=db.query(models.Cliente).count(),
        total_envios=db.query(models.Envio).count(),
    )


@router.get("/status", response_model=schemas.StatusOut)
def status(db: Session = Depends(get_db)):
    return _montar_status(db)


@router.patch("/settings/full", response_model=schemas.StatusOut)
def atualizar_full_runtime(
    body: schemas.FullRuntimePatch,
    db: Session = Depends(get_db),
    _=Depends(require_user),
):
    rc = db.get(models.RuntimeConfig, 1)
    if rc is None:
        rc = models.RuntimeConfig(
            id=1,
            full_scan_active=True,
            full_scan_interval_seconds=settings.full_scan_interval_seconds,
            full_scan_exec_time="08:00",
        )
        db.add(rc)
        db.flush()

    if body.full_scan_active is not None:
        rc.full_scan_active = body.full_scan_active
    if body.full_scan_interval_seconds is not None:
        rc.full_scan_interval_seconds = max(
            10, min(3600, body.full_scan_interval_seconds)
        )
    if body.full_scan_exec_time is not None:
        rc.full_scan_exec_time = body.full_scan_exec_time

    db.commit()
    db.refresh(rc)
    return _montar_status(db)


@router.patch("/settings/email-frases", response_model=schemas.StatusOut)
def atualizar_email_frases(
    body: schemas.EmailFrasesPatch,
    db: Session = Depends(get_db),
    _=Depends(require_user),
):
    rc = db.get(models.RuntimeConfig, 1)
    if rc is None:
        rc = models.RuntimeConfig(
            id=1,
            full_scan_active=True,
            full_scan_interval_seconds=settings.full_scan_interval_seconds,
            full_scan_exec_time="08:00",
            email_frases_dashboard=body.email_frases_dashboard.strip() or None,
        )
        db.add(rc)
    else:
        v = body.email_frases_dashboard.strip()
        rc.email_frases_dashboard = v or None
    db.commit()
    db.refresh(rc)
    return _montar_status(db)


@router.get("/health")
def health():
    return {"ok": True}
