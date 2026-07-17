from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Aurelia Boutique Enterprise API"
    environment: str = "development"
    secret_key: str = "dev-secret-change-me"
    access_token_minutes: int = 1440
    database_url: str = "sqlite:///./aurelia_boutique.db"
    cors_origins: str = "http://localhost:5173"
    admin_email: str = "admin@aureliaboutique.com"
    admin_password: str = "ChangeMe123!"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
