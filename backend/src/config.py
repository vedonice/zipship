from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application configuration"""

    # Database
    database_url: str = "postgresql://user:password@localhost:5432/cart_checkout"

    # JWT
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    token_expire_minutes: int = 30

    # Stripe
    stripe_api_key: str = "sk_test_..."
    stripe_webhook_secret: str = "whsec_test_..."

    # App
    debug: bool = False
    environment: str = "development"
    app_name: str = "ZipShip - Express Shopping Cart API"
    api_prefix: str = "/api/v1"

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
