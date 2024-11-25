# app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

class Settings(BaseSettings):
    OPN_SECRET_KEY: str = os.getenv("OPN_SECRET_KEY", "")
    OPN_PUBLIC_KEY: str = os.getenv("OPN_PUBLIC_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:mypaspostgressword@localhost:5432/water_db")

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

# For direct access to environment variables
settings = get_settings()
