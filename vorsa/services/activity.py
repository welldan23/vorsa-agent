"""Service riwayat aktivitas (tabel activity_logs)."""

import sqlite3

from vorsa.db.timeutil import from_db
from vorsa.ui.activity import ActivityEntry


def log_activity(
    conn: sqlite3.Connection, action: str, detail: str = "", user_id: int | None = None
) -> int:
    """Catat satu aksi (mis. "design_created", "published"). Mengembalikan id barisnya."""
    cur = conn.execute(
        "INSERT INTO activity_logs (user_id, action, detail) VALUES (?, ?, ?)",
        (user_id, action, detail),
    )
    conn.commit()
    return cur.lastrowid


def get_recent_activity(conn: sqlite3.Connection, limit: int = 10) -> list[ActivityEntry]:
    """Aktivitas terbaru dulu."""
    rows = conn.execute(
        "SELECT action, detail, created_at FROM activity_logs ORDER BY created_at DESC, id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    return [
        ActivityEntry(action=r["action"], detail=r["detail"] or "", created_at=from_db(r["created_at"]))
        for r in rows
    ]


def get_last_activity(conn: sqlite3.Connection) -> ActivityEntry | None:
    """Satu aktivitas paling baru, untuk baris "Aktivitas Terakhir" di Panel Utama."""
    recent = get_recent_activity(conn, limit=1)
    return recent[0] if recent else None
