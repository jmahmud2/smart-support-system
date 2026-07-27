"""
Application configuration.
All configurable values are centralized here.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""
    
    # API
    API_TITLE = os.getenv("API_TITLE", "Smart Support System API")
    API_VERSION = os.getenv("API_VERSION", "1.0.0")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))  # 24 hours
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # LLM
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-exp:free")
    
    # Rate Limiting
    RATE_LIMIT_RETRIES = int(os.getenv("RATE_LIMIT_RETRIES", 3))
    RATE_LIMIT_BACKOFF = int(os.getenv("RATE_LIMIT_BACKOFF", 2))
    
    # Pagination
    DEFAULT_PAGE_LIMIT = int(os.getenv("DEFAULT_PAGE_LIMIT", 20))
    MAX_PAGE_LIMIT = int(os.getenv("MAX_PAGE_LIMIT", 200))
    
    # CORS
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
    
    # Email
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "support@smart-support.com")