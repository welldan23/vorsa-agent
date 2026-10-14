from datetime import datetime, timedelta

from vorsa.db.timeutil import to_db
from vorsa.services.monitoring import get_monitoring_status

NOW = datetime(2026, 10, 14, 12, 0, 0)


def seed(db):
    db.executemany(
        "INSERT INTO categories (id, name, is_enabled) VALUES (?, ?, ?)",
        [(1, "Teknologi & AI", 1), (2, "Berita Nasional", 1), (3, "Tren Internet", 0)],
    )
    db.executemany(
        "INSERT INTO rss_sources (id, category_id, url, is_active, last_error) VALUES (?, ?, ?, ?, ?)",
        [
            (1, 1, "https://a/rss", 1, None),
            (2, 1, "https://b/rss", 1, None),
            (3, 2, "https://c/rss", 1, "Timeout 10 detik"),
            (4, 2, "https://d/rss", 0, "HTTP 404"),  # nonaktif: tidak dihitung
            (5, 3, "https://e/rss", 1, None),
        ],
    )


def add_run(db, started, finished):
    db.execute(
        "INSERT INTO check_runs (started_at, finished_at, status) VALUES (?, ?, 'success')",
        (to_db(started), to_db(finished) if finished else None),
    )


def add_article(db, n, category, fetched):
    db.execute(
        "INSERT INTO articles (source_id, category_id, title, link, content_hash, fetched_at)"
        " VALUES (?, ?, 'x', ?, ?, ?)",
        (1 if category == 1 else 3, category, f"l{n}", f"h{n}", to_db(fetched)),
    )


def test_no_runs_yet(db):
    seed(db)
    status = get_monitoring_status(db, 15, now=NOW)
    assert not status.bot_active
    assert status.last_checked_at is None and status.next_check_at is None
    assert [c.new_articles for c in status.categories] == [0, 0, 0]


def test_recent_run(db):
    seed(db)
    add_run(db, NOW - timedelta(minutes=40), NOW - timedelta(minutes=39))
    started = NOW - timedelta(minutes=6)
    add_run(db, started, started + timedelta(seconds=20))
    add_article(db, 1, 1, NOW - timedelta(minutes=30))  # putaran sebelumnya
    add_article(db, 2, 1, started + timedelta(seconds=5))
    add_article(db, 3, 2, started + timedelta(seconds=8))

    status = get_monitoring_status(db, 15, now=NOW)

    assert status.bot_active
    assert status.last_checked_at == started + timedelta(seconds=20)
    assert status.next_check_at == started + timedelta(minutes=15)
    tech, nasional, tren = status.categories
    assert (tech.name, tech.enabled, tech.active_sources, tech.failing_sources, tech.new_articles) == (
        "Teknologi & AI", True, 2, 0, 1,
    )
    assert (nasional.active_sources, nasional.failing_sources, nasional.new_articles) == (1, 1, 1)
    assert not tren.enabled


def test_stale_run_means_stopped(db):
    seed(db)
    add_run(db, NOW - timedelta(minutes=31), NOW - timedelta(minutes=30))
    status = get_monitoring_status(db, 15, now=NOW)
    assert not status.bot_active and status.next_check_at is None
    assert status.last_checked_at == NOW - timedelta(minutes=30)


def test_running_check_uses_start_time(db):
    seed(db)
    add_run(db, NOW - timedelta(minutes=1), None)
    assert get_monitoring_status(db, 15, now=NOW).last_checked_at == NOW - timedelta(minutes=1)
