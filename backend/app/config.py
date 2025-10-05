"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings with validation."""
    
    # App Info
    app_name: str = "SafeOutdoor API"
    version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    
    # Supabase
    supabase_url: str
    supabase_key: str
    
    # NASA Earthdata (OPeNDAP authentication) - Optional
    nasa_earthdata_user: Optional[str] = None
    nasa_earthdata_password: Optional[str] = None
    
    # OpenAQ
    openaq_api_key: str
    
    # Weather
    openweather_api_key: str
    
    # Mapbox
    mapbox_token: str
    
    # OpenAI
    openai_api_key: str
    
    # API Settings
    api_prefix: str = "/api"
    allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://safeoutdoor.app",
    ]
    
    # Request timeouts (seconds)
    http_timeout: int = 30
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
