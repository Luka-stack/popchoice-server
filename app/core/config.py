from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, computed_field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "PopChoice API"
    environment: Literal["local", "staging", "production"] = "local"
    debug: bool = False
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(default_factory=list)

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "popchoice"
    postgres_password: str = "popchoice"
    postgres_db: str = "popchoice"

    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800
    db_echo: bool = False

    openai_api_key: SecretStr | None = None
    openai_embedding_model: str = "text-embedding-ada-002"
    openai_recommendation_model: str = "gpt-5.4-mini"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.postgres_user,
                password=self.postgres_password,
                host=self.postgres_host,
                port=self.postgres_port,
                path=self.postgres_db,
            )
        )

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
