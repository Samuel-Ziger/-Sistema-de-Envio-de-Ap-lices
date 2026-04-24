"""FastAPI entrypoint."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import init_db, SessionLocal
from .auth import seed_admin
from .routers import clientes, envios, auth as auth_router, usuarios, status as status_router
from .services.full_watcher import watcher_global


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.ensure_dirs()
    init_db()
    # seed admin
    db = SessionLocal()
    try:
        seed_admin(db)
    finally:
        db.close()
    # inicia FULL watcher
    watcher_global.start()
    log.info("Backend pronto. auth_enabled=%s full_enabled=%s",
             settings.auth_enabled, settings.full_enabled)
    try:
        yield
    finally:
        watcher_global.stop()


app = FastAPI(
    title="Sistema de Envio de Apolices",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(status_router.router)
app.include_router(auth_router.router)
app.include_router(usuarios.router)
app.include_router(clientes.router)
app.include_router(envios.router)


@app.get("/", include_in_schema=False)
def root():
    return {
        "app": "Sistema de Envio de Apolices",
        "versao": "1.0.0",
        "docs": "/docs",
    }
