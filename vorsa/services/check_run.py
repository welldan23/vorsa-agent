"""Satu putaran pengecekan RSS: ambil → buang kembar → simpan → catat hasil di check_runs."""

import asyncio
import logging
import sqlite3

from vorsa.services import fetcher
from vorsa.services.dedup import store_entries

log = logging.getLogger(__name__)

# Mencegah dua putaran berjalan bersamaan (jadwal otomatis vs. "Cek Sekarang").
_lock = asyncio.Lock()


def is_check_running() -> bool:
    return _lock.locked()


def recover_interrupted_runs(conn: sqlite3.Connection) -> int:
    """Tandai putaran yang tertinggal 'running' (bot mati di tengah jalan) sebagai gagal."""
    with conn:
        cur = conn.execute(
            """
            UPDATE check_runs
            SET status = 'failed', finished_at = CURRENT_TIMESTAMP,
                error_message = 'Terhenti: bot mati di tengah pengecekan'
            WHERE status = 'running'
            """
        )
    return cur.rowcount


def _active_sources(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT s.id, s.url, s.category_id
        FROM rss_sources s JOIN categories c ON c.id = s.category_id
        WHERE s.is_active = 1 AND c.is_enabled = 1
        ORDER BY s.id
        """
    ).fetchall()


async def run_check(conn: sqlite3.Connection) -> int | None:
    """Jalankan satu putaran. Mengembalikan id check_runs, atau None kalau putaran lain masih jalan."""
    if is_check_running():
        log.info("Pengecekan dilewati: putaran sebelumnya masih berjalan")
        return None

    async with _lock:
        with conn:
            run_id = conn.execute("INSERT INTO check_runs DEFAULT VALUES").lastrowid
        try:
            sources = _active_sources(conn)
            category_of = {s["id"]: s["category_id"] for s in sources}
            results = await fetcher.fetch_all([(s["id"], s["url"]) for s in sources])

            new = duplicates = failed = 0
            for result in results:
                if result.ok:
                    stored = store_entries(conn, result.source_id, category_of[result.source_id], result.entries)
                    new += stored.new
                    duplicates += stored.duplicates
                else:
                    failed += 1
                with conn:
                    conn.execute(
                        """
                        UPDATE rss_sources
                        SET last_error = ?,
                            last_fetched_at = CASE WHEN ? IS NULL THEN CURRENT_TIMESTAMP ELSE last_fetched_at END
                        WHERE id = ?
                        """,
                        (result.error, result.error, result.source_id),
                    )

            if sources and failed == len(sources):
                status = "failed"
            elif failed:
                status = "partial"
            else:
                status = "success"
            with conn:
                conn.execute(
                    """
                    UPDATE check_runs
                    SET finished_at = CURRENT_TIMESTAMP, status = ?, sources_checked = ?,
                        sources_failed = ?, new_articles = ?, duplicates_skipped = ?
                    WHERE id = ?
                    """,
                    (status, len(sources), failed, new, duplicates, run_id),
                )
            log.info(
                "Pengecekan #%d %s: %d sumber, %d gagal, %d baru, %d kembar",
                run_id, status, len(sources), failed, new, duplicates,
            )
        except Exception as err:
            log.exception("Pengecekan #%d gagal total", run_id)
            with conn:
                conn.execute(
                    "UPDATE check_runs SET finished_at = CURRENT_TIMESTAMP, status = 'failed', error_message = ?"
                    " WHERE id = ?",
                    (f"{type(err).__name__}: {err}"[:500], run_id),
                )
        return run_id
