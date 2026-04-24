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
    full_enabled: bool
    full_watch_folder: str
    total_clientes: int
    total_envios: int
