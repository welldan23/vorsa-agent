"""Konfigurasi runtime dari .env."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    bot_token: str


def load_settings() -> Settings:
    load_dotenv()
    return Settings(bot_token=os.getenv("BOT_TOKEN", "").strip())
