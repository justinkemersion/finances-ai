"""Application configuration"""

import os
from typing import Optional


class Config:
    """Application configuration"""
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./finance_ai.db")
    SQL_ECHO: bool = os.getenv("SQL_ECHO", "false").lower() == "true"
    
    # Plaid Configuration
    PLAID_CLIENT_ID: Optional[str] = os.getenv("PLAID_CLIENT_ID")
    PLAID_SECRET: Optional[str] = os.getenv("PLAID_SECRET")
    PLAID_ENV: str = os.getenv("PLAID_ENV", "sandbox")  # sandbox, development, production
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    
    # Optional AI Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    USE_LOCAL_LLM: bool = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
    LOCAL_LLM_MODEL_PATH: Optional[str] = os.getenv("LOCAL_LLM_MODEL_PATH")


config = Config()
