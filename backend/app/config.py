"""Configurações carregadas do .env."""
from pathlib import Path
from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Servidor
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_debug: bool = False

    # Banco
    database_url: str = "sqlite:///./data/envio.db"

    # Auth
    auth_enabled: bool = False
    secret_key: str = "troque-essa-chave"
    access_token_expire_minutes: int = 480
    admin_username: str = "admin"
    admin_password: str = "admin123"

    # CORS
    cors_origins: str = "*"

    # SMTP (Brevo: use o relay SMTP com chave SMTP — não a API de “campanhas”, que é para listas sem anexo)
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = Field(
        default="",
        validation_alias=AliasChoices("SMTP_USER", "BREVO_SMTP_LOGIN"),
    )
    smtp_password: str = Field(
        default="",
        validation_alias=AliasChoices("SMTP_PASSWORD", "BREVO_SMTP_KEY"),
    )
    smtp_use_tls: bool = True
    smtp_from_email: str = Field(
        default="",
        validation_alias=AliasChoices("SMTP_FROM_EMAIL", "BREVO_SENDER_EMAIL"),
    )
    smtp_from_name: str = Field(
        default="Sistema de Envio",
        validation_alias=AliasChoices("SMTP_FROM_NAME", "BREVO_SENDER_NAME"),
    )
    use_brevo: bool = False

    @model_validator(mode="after")
    def _defaults_brevo(self):
        if self.use_brevo and not (self.smtp_host or "").strip():
            self.smtp_host = "smtp-relay.brevo.com"
            self.smtp_port = 587
            self.smtp_use_tls = True
        return self

    email_subject_default: str = "Envio de Apolice - {numero_apolice}"
    email_template_default: str = "templates/email_padrao.html"

    # FULL
    full_enabled: bool = True
    full_watch_folder: str = "./entrada"
    full_scan_interval_seconds: int = 30
    full_lote_size: int = 5
    full_intervalo_lote_min: int = 5
    full_rescan_horas: int = 1

    # Backup/pastas
    backup_folder: str = "./backup"
    upload_folder: str = "./uploads"
    processed_folder: str = "./processados"

    # Capa
    capa_enabled: bool = True
    capa_folder: str = "./capas"
    capa_arquivo_padrao: str = "capa.pdf"

    # Assinaturas e corpos de e-mail
    assinaturas_folder: str = "./assinaturas"

    @property
    def cors_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    def data_path(self, configured: str) -> Path:
        """Caminhos relativos no .env são sempre em relação à pasta backend/, não ao cwd."""
        p = Path(configured)
        if p.is_absolute():
            return p.resolve()
        return (BASE_DIR / p).resolve()

    def ensure_dirs(self) -> None:
        for rel in (
            self.backup_folder,
            self.upload_folder,
            self.processed_folder,
            self.full_watch_folder,
            self.capa_folder,
            self.assinaturas_folder,
        ):
            self.data_path(rel).mkdir(parents=True, exist_ok=True)
        if self.database_url.startswith("sqlite:///"):
            db_path = Path(self.database_url.replace("sqlite:///", "", 1))
            if not db_path.is_absolute():
                db_path = (BASE_DIR / db_path).resolve()
            db_path.parent.mkdir(parents=True, exist_ok=True)


settings = Settings()
