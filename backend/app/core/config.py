from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path

# This resolves to C:\Projects\serviceflow\backend\.env
# No matter where uvicorn is launched from
ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    APP_NAME: str = "ServiceFlow CRM"
    APP_ENV: str = "development"
    DEBUG: bool = True

    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    ALLOWED_ORIGINS: str = "http://localhost"

    def get_allowed_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    model_config = {"env_file": str(ENV_FILE), "env_file_encoding": "utf-8"}


settings = Settings()