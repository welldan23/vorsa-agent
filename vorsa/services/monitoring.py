"""Service status pemantauan: dibangun dari check_runs, categories, dan rss_sources."""

import sqlite3
from datetime import datetime, timedelta

from vorsa.db.timeutil import from_db
from vorsa.ui.status import CategoryStatus, MonitoringStatus

# Pemantauan dianggap berhenti kalau tidak ada pengecekan selama 2× interval.
STALE_FACTOR = 2


def get_latest_check_run(conn: sqlite3.Connection) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM check_runs ORDER BY started_at DESC, id DESC LIMIT 1").fetchone()


def get_monitoring_status(
    conn: sqlite3.Connection, interval_minutes: int, now: datetime | None = None
) -> MonitoringStatus:
    now = now or datetime.now()
    run = get_latest_check_run(conn)
    started = from_db(run["started_at"]) if run else None
    last_checked = (from_db(run["finished_at"]) or started) if run else None
    interval = timedelta(minutes=interval_minutes)
    active = started is not None and now - started <= interval * STALE_FACTOR

    # Berita baru per kategori = yang diambil sejak putaran terakhir dimulai.
    since = run["started_at"] if run else None
    rows = conn.execute(
        """
        SELECT c.name, c.is_enabled,
               (SELECT COUNT(*) FROM rss_sources s
                 WHERE s.category_id = c.id AND s.is_active = 1) AS active_sources,
               (SELECT COUNT(*) FROM rss_sources s
                 WHERE s.category_id = c.id AND s.is_active = 1 AND s.last_error IS NOT NULL) AS failing,
               (SELECT COUNT(*) FROM articles a
                 WHERE a.category_id = c.id AND ? IS NOT NULL AND a.fetched_at >= ?) AS new_articles
        FROM categories c
        ORDER BY c.id
        """,
        (since, since),
    ).fetchall()

    return MonitoringStatus(
        bot_active=active,
        interval_minutes=interval_minutes,
        last_checked_at=last_checked,
        next_check_at=started + interval if active else None,
        categories=[
            CategoryStatus(
                name=r["name"],
                enabled=bool(r["is_enabled"]),
                active_sources=r["active_sources"],
                failing_sources=r["failing"],
                new_articles=r["new_articles"],
            )
            for r in rows
        ],
    )
