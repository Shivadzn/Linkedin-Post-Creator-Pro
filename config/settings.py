"""
Configuration settings for the LinkedIn Post Generator.
Uses Pydantic for type-safe environment variable management.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Groq API Configuration
    groq_api_key: str = Field(..., env="GROQ_API_KEY", description="Groq API key")
    groq_model: str = Field(default="llama3-8b-8192", env="GROQ_MODEL", description="Groq model to use")
    
    # Application Settings
    max_post_length: int = Field(default=1000, env="MAX_POST_LENGTH", description="Maximum post length")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL", description="Cache TTL in seconds")
    log_level: str = Field(default="INFO", env="LOG_LEVEL", description="Logging level")
    
    # Optional: Redis Configuration
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL", description="Redis URL for caching")
    
    # Optional: Rate Limiting
    max_requests_per_minute: int = Field(default=10, env="MAX_REQUESTS_PER_MINUTE", description="Rate limit per minute")
    
    # Data Paths
    raw_data_path: str = Field(default="data/raw_post.json", description="Path to raw data")
    processed_data_path: str = Field(default="data/processed_posts.json", description="Path to processed data")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings 