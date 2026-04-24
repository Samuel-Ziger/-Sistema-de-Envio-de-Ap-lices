"""Modelos ORM (SQLAlchemy)."""
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    cpf: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    cnpj: Mapped[str | None] = mapped_column(String(25), nullable=True, index=True)
    telefone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    envios: Mapped[list["Envio"]] = relationship(
        back_populates="cliente", cascade="all, delete-orphan"
    )


class Envio(Base):
    __tablename__ = "envios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), index=True)
    tipo_envio: Mapped[str] = mapped_column(String(20), nullable=False)  # FULL | AVULSO
    nome_arquivo_original: Mapped[str | None] = mapped_column(String(500), nullable=True)
    nome_arquivo_final: Mapped[str | None] = mapped_column(String(500), nullable=True)
    numero_apolice: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="pendente")  # pendente|enviado|erro
    erro_msg: Mapped[str | None] = mapped_column(Text, nullable=True)
    caminho_backup: Mapped[str | None] = mapped_column(String(500), nullable=True)
    assunto_email: Mapped[str | None] = mapped_column(String(500), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    enviado_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    cliente: Mapped["Cliente"] = relationship(back_populates="envios")


class RuntimeConfig(Base):
    """Configuração em tempo de execução (uma linha, id=1). Controla o watcher FULL pelo painel."""

    __tablename__ = "runtime_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_scan_active: Mapped[bool] = mapped_column(Boolean, default=True)
    full_scan_interval_seconds: Mapped[int] = mapped_column(Integer, default=30)
    # Horário diário de execução do FULL (HH:MM). Ex.: "08:30"
    full_scan_exec_time: Mapped[str | None] = mapped_column(String(5), nullable=True)
    # Texto extra no corpo HTML de todos os envios (definido no Dashboard)
    email_frases_dashboard: Mapped[str | None] = mapped_column(Text, nullable=True)


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
