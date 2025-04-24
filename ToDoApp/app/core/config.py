# ToDoApp/app/core/config.py
import os
from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "ToDoApp"
    APP_VERSION: str = "0.1.0"

    # Security settings - load from environment
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database settings
    DATABASE_URL: str

    # Consul settings
    CONSUL_HOST: str = "localhost"
    CONSUL_PORT: int = 8500
    CONSUL_ENABLED: bool = False

    # Service settings
    SERVICE_HOST: str = "0.0.0.0"
    SERVICE_PORT: int = 8080

    class Config:
        env_file = ".env"


settings = Settings()