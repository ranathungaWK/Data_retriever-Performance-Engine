from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    
    VICTORIA_URL: str 
    VICTORIA_TIMEOUT_SECONDS: int = 30

    DATABASE_URL: PostgresDsn

    GRAFANA_URL: str

    model_config = SettingsConfigDict(
        env_file=".env" ,
        case_sensitive=True,
        extra="ignore"
    )

    @field_validator("VICTORIA_URL" , "GRAFANA_URL")
    @classmethod
    def validate_urls(cls , v: str) -> str:
        if not v.startswith(("http://" , "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v.rstrip("/")

settings = Settings()

