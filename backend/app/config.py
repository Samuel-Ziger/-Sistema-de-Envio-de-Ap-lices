"""Configurações carregadas do .env."""
from pathlib import Path
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

    # SMTP
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    smtp_from_email: str = ""
    smtp_from_name: str = "Sistema de Envio"

    email_subject_default: str = "Envio de Apolice - {numero_apolice}"
    email_template_default: str = "templates/email_padrao.html"

    # FULL
    full_enabled: bool = True
    full_watch_folder: str = "./entrada"
    full_scan_interval_seconds: int = 30

    # Backup/pastas
    backup_folder: str = "./backup"
    upload_folder: str = "./uploads"
    processed_folder: str = "./processados"

    @property
    def cors_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    def ensure_dirs(self) -> None:
        for rel in (
            self.backup_folder,
            self.upload_folder,
            self.processed_folder,
            self.full_watch_folder,
        ):
            Path(rel).mkdir(parents=True, exist_ok=True)
        # pasta do SQLite
        if self.database_url.startswith("sqlite:///"):
            db_path = Path(self.database_url.replace("sqlite:///", "", 1))
            db_path.parent.mkdir(parents=True, exist_ok=True)


settings = Settings()
