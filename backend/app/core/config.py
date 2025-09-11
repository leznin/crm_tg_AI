import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "mysql+pymysql://root:696578As@localhost/tg_crm?charset=utf8mb4"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # CSRF
    CSRF_SECRET: str = "csrf-secret-key-change-in-production"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Admin credentials
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASS: str = "admin123"
    
    # Telegram Bot (deprecated - now stored in database)
    TELEGRAM_BOT_TOKEN: str = "your_telegram_bot_token"
    
    # Encryption settings
    ENCRYPTION_KEY: str = "encryption-key-change-in-production"  # Used for API key encryption

    class Config:
        env_file = ".env"

settings = Settings()