"""Konversi waktu antara database (teks UTC) dan tampilan (waktu lokal server)."""

from datetime import datetime, timezone

DB_FORMAT = "%Y-%m-%d %H:%M:%S"


def to_db(value: datetime) -> str:
    """datetime → teks UTC untuk disimpan. Datetime naif dianggap waktu lokal."""
    return value.astimezone(timezone.utc).strftime(DB_FORMAT)


def from_db(value: str | None) -> datetime | None:
    """Teks UTC dari database → datetime lokal naif (dipakai tampilan)."""
    if not value:
        return None
    return datetime.fromisoformat(value).replace(tzinfo=timezone.utc).astimezone().replace(tzinfo=None)


def local_midnight_db(now: datetime | None = None) -> str:
    """Awal hari ini (waktu lokal) dalam format database, untuk filter "hari ini"."""
    now = now or datetime.now()
    return to_db(now.replace(hour=0, minute=0, second=0, microsecond=0))
