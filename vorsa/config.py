"""Konfigurasi runtime dari .env."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    bot_token: str
    database_path: str
    check_interval_minutes: int


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        bot_token=os.getenv("BOT_TOKEN", "").strip(),
        database_path=os.getenv("DATABASE_PATH", "data/vorsa.sqlite3").strip(),
        check_interval_minutes=int(os.getenv("CHECK_INTERVAL_MINUTES", "15")),
    )
