"""
Configuration settings for the LLM Document Processing System
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    API_SECRET_KEY: str = Field(default="dev-secret-key", env="API_SECRET_KEY")
    BEARER_TOKEN: str = Field(default="dev-bearer-token", env="BEARER_TOKEN")
    
    # Google Gemini Configuration
    GEMINI_API_KEY: str = Field(env="GEMINI_API_KEY")
    GEMINI_MODEL: str = Field(default="gemini-1.5-pro", env="GEMINI_MODEL")
    GEMINI_EMBEDDING_MODEL: str = Field(default="models/text-embedding-004", env="GEMINI_EMBEDDING_MODEL")
    
    # Vector Database Configuration
    VECTOR_DB_TYPE: str = Field(default="faiss", env="VECTOR_DB_TYPE")
    VECTOR_DB_PATH: str = Field(default="./data/vector_db", env="VECTOR_DB_PATH")
    EMBEDDING_DIMENSION: int = Field(default=768, env="EMBEDDING_DIMENSION")
    
    # Document Processing Configuration
    MAX_DOCUMENT_SIZE_MB: int = Field(default=50, env="MAX_DOCUMENT_SIZE_MB")
    SUPPORTED_FORMATS: str = Field(default="pdf,docx,doc,txt,html", env="SUPPORTED_FORMATS")
    CHUNK_SIZE: int = Field(default=1000, env="CHUNK_SIZE")
    CHUNK_OVERLAP: int = Field(default=200, env="CHUNK_OVERLAP")
    
    # Performance Configuration
    MAX_CONCURRENT_DOWNLOADS: int = Field(default=5, env="MAX_CONCURRENT_DOWNLOADS")
    RESPONSE_TIMEOUT_SECONDS: int = Field(default=30, env="RESPONSE_TIMEOUT_SECONDS")
    CACHE_TTL_SECONDS: int = Field(default=3600, env="CACHE_TTL_SECONDS")
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field(default="./logs/app.log", env="LOG_FILE")
    
    @property
    def supported_formats_list(self) -> List[str]:
        """Get supported formats as a list"""
        return [fmt.strip().lower() for fmt in self.SUPPORTED_FORMATS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
