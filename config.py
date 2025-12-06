from functools import lru_cache
from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from pydantic import Field
import os 

from dotenv import load_dotenv
env_path = ".env.test" if os.environ.get("PYTEST_CURRENT_TEST") else ".env"
load_dotenv(dotenv_path= env_path)

# env_path =None
# if "PYTEST_CURRENT_TEST" in os.environ:
#     env_path = ".env.test"
# else:
#     env_path = ".env"

# 
class Settings(BaseSettings):
    # Конфигурация Pydantic V2
    model_config = ConfigDict(
        env_file=env_path,
        env_file_encoding="utf-8",
    )

    # Админские секреты
    SECRET_ADMIN: str
    SECRET_ADMIN_EMAIL: str

    # База данных
    DATABASE_URL: str

    # Сервер
    SERVER_PORT: int

    # Redis
    REDIS_URL: str

    # JWT
    SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    ALGORITHM: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24  # значение по умолчанию

    # SMTP
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str
    SECRET_EMAIL: str

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    # CORS
    CORS_ORIGINS: str


# default_settings = Settings()

@lru_cache
def get_settings() -> Settings:
    return Settings()






