from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuracoes da aplicacao carregadas de variaveis de ambiente."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    redis_url: str = "redis://redis_broker:6379/0"
    redis_result_url: str = "redis://redis_broker:6379/1"
    model_store_path: str = "/app/models/demand_forecaster.joblib"
    dataset_store_path: str = "/app/datasets"
    default_budget_limit: str = "1000.00"
    default_cycle_weeks: int = 4
    default_random_seed: int = 42
    progress_every_generations: int = 10
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    log_level: str = "INFO"

    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
