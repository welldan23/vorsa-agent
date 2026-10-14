"""Service pengguna yang diizinkan memakai bot (tabel users)."""

import sqlite3


def sync_owners(conn: sqlite3.Connection, telegram_ids: tuple[str, ...]) -> None:
    """Samakan daftar pemilik dengan konfigurasi.

    ID di daftar menjadi owner aktif; owner lama yang tidak ada di daftar dinonaktifkan.
    Pengguna ber-role lain (admin) tidak disentuh.
    """
    with conn:
        for telegram_id in telegram_ids:
            conn.execute(
                """
                INSERT INTO users (telegram_id, role, is_active) VALUES (?, 'owner', 1)
                ON CONFLICT (telegram_id) DO UPDATE SET role = 'owner', is_active = 1
                """,
                (telegram_id,),
            )
        placeholders = ",".join("?" * len(telegram_ids))
        conn.execute(
            f"UPDATE users SET is_active = 0 WHERE role = 'owner' AND telegram_id NOT IN ({placeholders})",
            telegram_ids,
        )


def get_active_user(conn: sqlite3.Connection, telegram_id: int | str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM users WHERE telegram_id = ? AND is_active = 1", (str(telegram_id),)
    ).fetchone()


def remember_name(conn: sqlite3.Connection, user_id: int, name: str | None) -> None:
    """Simpan nama tampilan Telegram kalau berubah."""
    if name:
        with conn:
            conn.execute("UPDATE users SET name = ? WHERE id = ? AND name IS NOT ?", (name, user_id, name))
