from typing import ClassVar

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    API_VERSION: float = 1.0
    API_PORT: int = 8000
    API_URL: ClassVar[str] = "http://localhost:8000${API_V1_STR}"
    API_V1_STR: str = "/v1"
    
    SECRET_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8 # 8 days
    
    @model_validator(mode="after")
    def _require_secret_key(self) -> "Settings":
        if not self.SECRET_KEY:
            raise ValueError(
                "SECRET_KEY is not set. Add it to your .env file.\n"
            )
        return self
    
env = Settings()