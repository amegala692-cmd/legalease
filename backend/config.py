from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LegalEase"
    app_version: str = "1.0.0"
    environment: str = "development"
    backend_host: str = "127.0.0.1"
    backend_port: int = 8000
    frontend_url: str = "http://localhost:8501"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"
    generation_temperature: float = 0.25
    generation_max_tokens: int = 8192
    allow_demo_mode: bool = True
    max_request_chars: int = 50000
    company_name: str = "LegalEase"
    default_footer: str = "Generated with LegalEase — informational use only; not legal advice."

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
