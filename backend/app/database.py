"""Setup do SQLAlchemy + SQLite."""
from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from typing import Generator

from .config import BASE_DIR, settings


class Base(DeclarativeBase):
    pass


def _database_url_resolvida() -> str:
    """SQLite relativo ao cwd passa a ser relativo à pasta backend/."""
    u = settings.database_url
    if not u.startswith("sqlite:///"):
        return u
    rest = u.replace("sqlite:///", "", 1)
    p = Path(rest)
    if p.is_absolute():
        return u
    abs_p = (BASE_DIR / p).resolve()
    return f"sqlite:///{abs_p.as_posix()}"


# SQLite precisa de connect_args={"check_same_thread": False}
engine_kwargs = {"future": True}
_db_url = _database_url_resolvida()
if _db_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(_db_url, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Cria tabelas se não existirem."""
    from . import models  # noqa: F401  (garante registro dos models)

    Base.metadata.create_all(bind=engine)
    _migrate_runtime_config_columns()
    _seed_runtime_config()


def _migrate_runtime_config_columns() -> None:
    """SQLite: adiciona colunas novas a runtime_config sem Alembic."""
    insp = inspect(engine)
    if "runtime_config" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("runtime_config")}
    with engine.begin() as conn:
        if "email_frases_dashboard" not in cols:
            conn.execute(
                text("ALTER TABLE runtime_config ADD COLUMN email_frases_dashboard TEXT")
            )


def _seed_runtime_config() -> None:
    """Garante linha única de configuração runtime (FULL pelo painel)."""
    from . import models

    s = SessionLocal()
    try:
        row = s.get(models.RuntimeConfig, 1)
        if row is None:
            s.add(
                models.RuntimeConfig(
                    id=1,
                    full_scan_active=True,
                    full_scan_interval_seconds=settings.full_scan_interval_seconds,
                )
            )
            s.commit()
    finally:
        s.close()
