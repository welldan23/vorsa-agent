"""Tingkat penyaringan: ambang relevansi per kategori (categories.min_relevance)."""

import sqlite3

from vorsa.services.activity import log_activity
from vorsa.services.categories import get_category

# nama preset → ambang untuk semua kategori
PRESETS = {"longgar": 0.55, "normal": 0.70, "ketat": 0.85}
STEP = 0.05
MIN_THRESHOLD = 0.30
MAX_THRESHOLD = 0.95


def clamp(value: float) -> float:
    return round(min(MAX_THRESHOLD, max(MIN_THRESHOLD, value)), 2)


def current_preset(thresholds: list[float]) -> str | None:
    """Nama preset kalau semua kategori memakai ambang preset yang sama; selain itu None."""
    values = set(thresholds)
    if len(values) != 1:
        return None
    (value,) = values
    return next((name for name, v in PRESETS.items() if abs(v - value) < 1e-9), None)


def apply_preset(conn: sqlite3.Connection, preset: str, user_id: int | None = None) -> float:
    value = PRESETS[preset]
    with conn:
        conn.execute("UPDATE categories SET min_relevance = ?", (value,))
    log_activity(conn, "filter_changed", f"Semua kategori: {preset.capitalize()} ({value:.0%})", user_id=user_id)
    return value


def adjust_threshold(
    conn: sqlite3.Connection, category_id: int, delta: float, user_id: int | None = None
) -> float | None:
    """Naik/turunkan ambang satu kategori. None kalau kategorinya tidak ada."""
    category = get_category(conn, category_id)
    if category is None:
        return None
    value = clamp(category.min_relevance + delta)
    if value != category.min_relevance:
        with conn:
            conn.execute("UPDATE categories SET min_relevance = ? WHERE id = ?", (value, category_id))
        log_activity(conn, "filter_changed", f"{category.name}: {value:.0%}", user_id=user_id)
    return value
