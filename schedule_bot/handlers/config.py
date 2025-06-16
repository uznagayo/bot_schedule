import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from aiogram.fsm.storage.memory import MemoryStorage

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "schedule.db")
DB_PATH = os.path.abspath(DB_PATH)

storage = MemoryStorage()

channel_id = -1002893005429


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
    bot_token: str


settings = Settings()
