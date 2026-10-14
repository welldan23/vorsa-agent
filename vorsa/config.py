"""Konfigurasi runtime dari .env."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    bot_token: str
    database_path: str
    check_interval_minutes: int
    owner_telegram_ids: tuple[str, ...] = ()  # pemilik yang boleh memakai bot


def _parse_ids(raw: str) -> tuple[str, ...]:
    """ "123, 456" → ("123", "456"); entri yang bukan angka diabaikan."""
    return tuple(dict.fromkeys(part.strip() for part in raw.split(",") if part.strip().isdigit()))


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        bot_token=os.getenv("BOT_TOKEN", "").strip(),
        database_path=os.getenv("DATABASE_PATH", "data/vorsa.sqlite3").strip(),
        check_interval_minutes=int(os.getenv("CHECK_INTERVAL_MINUTES", "15")),
        owner_telegram_ids=_parse_ids(os.getenv("OWNER_TELEGRAM_IDS", "")),
    )
