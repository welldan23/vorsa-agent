"""Titik masuk.

    python -m vorsa            jalankan bot
    python -m vorsa --preview  cetak Panel Utama di terminal (tanpa token)
    python -m vorsa --migrate  siapkan/perbarui database saja
"""

import asyncio
import logging
import re
import sqlite3
import sys

from vorsa.config import Settings, load_settings


def preview() -> None:
    from vorsa.keyboards.panel import main_panel_keyboard
    from vorsa.stub.mock_data import get_panel_snapshot
    from vorsa.ui.panel import render_main_panel

    text = render_main_panel(get_panel_snapshot(), "Pemilik")
    print(re.sub(r"</?[bi]>", "", text))
    print()
    for row in main_panel_keyboard().inline_keyboard:
        print("  ".join(f"[ {btn.text} ]" for btn in row))


async def run_bot(settings: Settings, db: sqlite3.Connection) -> None:
    from vorsa.bot import create_bot, create_dispatcher, register_commands

    bot = create_bot(settings.bot_token)
    dp = create_dispatcher(db, settings)
    await register_commands(bot)
    await dp.start_polling(bot)


def open_database(database_path: str) -> sqlite3.Connection:
    from vorsa.db.connection import connect
    from vorsa.db.migrate import apply_migrations

    conn = connect(database_path)
    version = apply_migrations(conn)
    logging.info("Database %s siap (skema versi %d)", database_path, version)
    return conn


def main() -> None:
    if "--preview" in sys.argv:
        preview()
        return

    logging.basicConfig(level=logging.INFO)
    settings = load_settings()
    db = open_database(settings.database_path)
    try:
        if "--migrate" in sys.argv:
            return
        if not settings.bot_token:
            sys.exit("BOT_TOKEN belum diisi. Salin .env.example jadi .env lalu isi token dari @BotFather.")
        asyncio.run(run_bot(settings, db))
    finally:
        db.close()


if __name__ == "__main__":
    main()
