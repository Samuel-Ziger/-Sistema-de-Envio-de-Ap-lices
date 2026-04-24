"""Schemas Pydantic (entrada/saída da API)."""
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ========= Cliente =========
class ClienteBase(BaseModel):
    nome: str
    email: EmailStr
    cpf: str | None = None
    cnpj: str | None = None
    telefone: str | None = None
    observacoes: str | None = None
    ativo: bool = True


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nome: str | None = None
    email: EmailStr | None = None
    cpf: str | None = None
    cnpj: str | None = None
    telefone: str | None = None
    observacoes: str | None = None
    ativo: bool | None = None


class ClienteOut(ClienteBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ========= Envio =========
class EnvioOut(BaseModel):
    id: int
    cliente_id: int
    tipo_envio: str
    nome_arquivo_original: str | None
    nome_arquivo_final: str | None
    numero_apolice: str | None
    status: str
    erro_msg: str | None
    assunto_email: str | None
    criado_em: datetime
    enviado_em: datetime | None
    model_config = ConfigDict(from_attributes=True)


class EnvioAvulsoPayload(BaseModel):
    cliente_id: int | None = None
    # se quiser criar cliente no mesmo request:
    cliente_novo: ClienteCreate | None = None
    numero_apolice: str | None = None
    assunto: str | None = None
    mensagem: str | None = None


# ========= Usuário =========
class UsuarioBase(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    nome: str
    email: str | None = None
    is_admin: bool = False
    ativo: bool = True


class UsuarioCreate(UsuarioBase):
    senha: str = Field(min_length=4)


class UsuarioUpdate(BaseModel):
    nome: str | None = None
    email: str | None = None
    is_admin: bool | None = None
    ativo: bool | None = None
    senha: str | None = None


class UsuarioOut(UsuarioBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ========= Auth =========
class LoginPayload(BaseModel):
    username: str
    senha: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UsuarioOut


# ========= Status =========
class StatusOut(BaseModel):
    status: str
    versao: str
    auth_enabled: bool
    # FULL: full_enabled = ativo de facto (.env FULL_ENABLED e interruptor do painel)
    full_enabled: bool
    full_env_enabled: bool
    full_scan_active: bool
    full_scan_interval_seconds: int
    full_scan_exec_time: str = "08:00"
    full_watch_folder: str
    # Frases extra no corpo do e-mail (painel)
    email_frases_dashboard: str = ""
    total_clientes: int
    total_envios: int


class FullRuntimePatch(BaseModel):
    """Atualização parcial do modo FULL (painel)."""

    full_scan_active: bool | None = None
    full_scan_interval_seconds: int | None = Field(None, ge=10, le=3600)
    full_scan_exec_time: str | None = Field(
        None,
        pattern=r"^([01]\d|2[0-3]):[0-5]\d$",
        description="Horário diário do FULL no formato HH:MM",
    )


class EmailFrasesPatch(BaseModel):
    """Texto extra incluído no corpo HTML de todos os envios."""

    email_frases_dashboard: str = Field(default="", max_length=12000)
