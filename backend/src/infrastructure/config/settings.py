"""Configurações de ambiente carregadas com Python puro (stdlib), sem acoplamento a bibliotecas externas."""

from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path


def _load_dotenv_file(env_path: str = ".env") -> None:
    """Leitor leve de arquivo .env usando apenas biblioteca padrão do Python."""
    path = Path(env_path)
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


@dataclass(frozen=True)
class Settings:
    """Configurações imutáveis da aplicação."""

    app_name: str
    app_env: str
    debug: bool
    cors_allowed_origins: list[str]
    mongodb_uri: str
    mongodb_db_name: str
    jwt_secret_key: str
    jwt_algorithm: str
    jwt_access_token_expire_minutes: int


@lru_cache
def get_settings() -> Settings:
    _load_dotenv_file()
    debug_raw = os.getenv("DEBUG", "true").strip().lower()
    raw_origins = os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:5173",
    )
    allowed_origins = [
        origin.strip() for origin in raw_origins.split(",") if origin.strip()
    ]
    return Settings(
        app_name=os.getenv("APP_NAME", "Passa o Bastão API"),
        app_env=os.getenv("APP_ENV", "development"),
        debug=debug_raw in {"1", "true", "yes"},
        cors_allowed_origins=allowed_origins,
        mongodb_uri=os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
        mongodb_db_name=os.getenv("MONGODB_DB_NAME", "passa_o_bastao"),
        jwt_secret_key=os.getenv(
            "JWT_SECRET_KEY",
            "dev-secret-key-change-in-production-min-32-bytes",
        ),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        jwt_access_token_expire_minutes=int(
            os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "120")
        ),
    )
