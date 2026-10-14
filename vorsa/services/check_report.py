"""Ringkasan hasil pengecekan untuk hub Pantau Berita dan laporan "Cek Terakhir"."""

import sqlite3
from datetime import datetime

from vorsa.db.timeutil import from_db, local_midnight_db
from vorsa.services.monitoring import get_latest_check_run, get_monitoring_status
from vorsa.services.news import count_important_today
from vorsa.ui.check_run import CheckRun, SourceFailure
from vorsa.ui.monitor import MonitorOverview


def _failing_sources(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """Sumber aktif (di kategori aktif) yang gagal pada pengambilan terakhirnya."""
    return conn.execute(
        """
        SELECT s.url, s.last_error, c.name AS category
        FROM rss_sources s JOIN categories c ON c.id = s.category_id
        WHERE s.is_active = 1 AND c.is_enabled = 1 AND s.last_error IS NOT NULL
        ORDER BY s.id
        """
    ).fetchall()


def get_last_check_report(
    conn: sqlite3.Connection, interval_minutes: int, now: datetime | None = None
) -> CheckRun | None:
    run = get_latest_check_run(conn)
    if run is None:
        return None
    status = get_monitoring_status(conn, interval_minutes, now=now)
    per_category = {c.name: c.new_articles for c in status.categories if c.enabled}
    return CheckRun(
        started_at=from_db(run["started_at"]),
        finished_at=from_db(run["finished_at"]),
        next_check_at=status.next_check_at,
        interval_minutes=interval_minutes,
        sources_checked=run["sources_checked"],
        failures=[
            SourceFailure(url=r["url"], category=r["category"], error=r["last_error"])
            for r in _failing_sources(conn)
        ],
        new_articles=run["new_articles"],
        duplicates_skipped=run["duplicates_skipped"],
        passed_filter=run["passed_filter"],
        new_per_category=per_category,
        error=run["error_message"] if run["status"] == "failed" else None,
    )


def get_monitor_overview(
    conn: sqlite3.Connection, interval_minutes: int, now: datetime | None = None
) -> MonitorOverview:
    status = get_monitoring_status(conn, interval_minutes, now=now)
    enabled = [c for c in status.categories if c.enabled]
    midnight = local_midnight_db(now)
    fetched_today = conn.execute("SELECT COUNT(*) FROM articles WHERE fetched_at >= ?", (midnight,)).fetchone()[0]
    duplicates_today = conn.execute(
        "SELECT COALESCE(SUM(duplicates_skipped), 0) FROM check_runs WHERE started_at >= ?", (midnight,)
    ).fetchone()[0]
    return MonitorOverview(
        running=status.bot_active,
        interval_minutes=interval_minutes,
        last_checked_at=status.last_checked_at,
        next_check_at=status.next_check_at,
        active_categories=len(enabled),
        total_categories=len(status.categories),
        active_sources=sum(c.active_sources for c in enabled),
        failing_sources=sum(c.failing_sources for c in enabled),
        fetched_today=fetched_today,
        duplicates_skipped_today=duplicates_today,
        important_today=count_important_today(conn),
    )


def count_sources_to_check(conn: sqlite3.Connection) -> int:
    return conn.execute(
        """
        SELECT COUNT(*) FROM rss_sources s JOIN categories c ON c.id = s.category_id
        WHERE s.is_active = 1 AND c.is_enabled = 1
        """
    ).fetchone()[0]
