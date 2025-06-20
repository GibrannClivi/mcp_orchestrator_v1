"""
Configuration loader for the MCP Orchestrator.
Loads all settings from environment variables using python-dotenv.
"""
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Load .env file if present
load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )
    ENV: str = Field(default="development")
    PROJECT_NAME: str = Field(default="mcp-orchestrator")
    PORT: int = Field(default=8080)
    GOOGLE_CLOUD_PROJECT: str = Field(default="")
    GOOGLE_APPLICATION_CREDENTIALS: str = Field(default="")
    GOOGLE_CLOUD_RUN_REGION: str = Field(default="")
    VERTEXAI_PROJECT_ID: str = Field(default="")
    VERTEXAI_LOCATION: str = Field(default="")
    VERTEXAI_MODEL_NAME: str = Field(default="gemma-3-9b-it-e4b")
    FIRESTORE_PROJECT_ID: str = Field(default="")
    FIRESTORE_COLLECTION: str = Field(default="orchestrator_cache")
    GOOGLE_SECRET_MANAGER_PROJECT_ID: str = Field(default="")
    CORS_ALLOW_ORIGINS: str = Field(default="*")
    LOG_LEVEL: str = Field(default="INFO")
    CACHE_TTL_SECONDS: int = Field(default=300)

settings = Settings()
