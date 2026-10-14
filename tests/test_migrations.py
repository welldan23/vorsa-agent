import sqlite3

import pytest

from vorsa.db import migrate
from vorsa.db.connection import connect


@pytest.fixture
def conn():
    c = connect(":memory:")
    yield c
    c.close()


def tables(conn):
    return {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}


def test_creates_panel_tables(conn):
    assert migrate.apply_migrations(conn) == len(migrate.list_migrations())
    assert {"users", "categories", "rss_sources", "articles", "check_runs", "activity_logs"} <= tables(conn)


def test_is_idempotent(conn):
    version = migrate.apply_migrations(conn)
    assert migrate.apply_migrations(conn) == version


def test_article_constraints(db):
    conn = db
    conn.execute("INSERT INTO categories (id, name) VALUES (1, 'Teknologi & AI')")
    conn.execute("INSERT INTO rss_sources (id, category_id, url) VALUES (1, 1, 'https://x/rss')")
    insert = (
        "INSERT INTO articles (source_id, category_id, title, link, content_hash, relevance_score)"
        " VALUES (1, 1, ?, ?, ?, ?)"
    )
    conn.execute(insert, ("A", "https://x/a", "h1", 0.9))
    row = conn.execute("SELECT is_important, is_flagged, fetched_at FROM articles").fetchone()
    assert (row["is_important"], row["is_flagged"]) == (0, 0) and row["fetched_at"]

    with pytest.raises(sqlite3.IntegrityError):  # link kembar
        conn.execute(insert, ("B", "https://x/a", "h2", 0.5))
    with pytest.raises(sqlite3.IntegrityError):  # isi kembar
        conn.execute(insert, ("C", "https://x/c", "h1", 0.5))
    with pytest.raises(sqlite3.IntegrityError):  # skor di luar 0–1
        conn.execute(insert, ("D", "https://x/d", "h4", 1.5))
    with pytest.raises(sqlite3.IntegrityError):  # sumber tidak ada
        conn.execute(insert.replace("VALUES (1, 1,", "VALUES (99, 1,"), ("E", "https://x/e", "h5", 0.5))


def test_deleting_source_removes_its_articles(db):
    conn = db
    conn.execute("INSERT INTO categories (id, name) VALUES (1, 'Teknologi & AI')")
    conn.execute("INSERT INTO rss_sources (id, category_id, url) VALUES (1, 1, 'https://x/rss')")
    conn.execute(
        "INSERT INTO articles (source_id, category_id, title, link, content_hash) VALUES (1, 1, 'A', 'l', 'h')"
    )
    conn.execute("DELETE FROM rss_sources WHERE id = 1")
    assert conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0] == 0


def test_check_run_status_and_activity_defaults(conn):
    migrate.apply_migrations(conn)
    conn.execute("INSERT INTO check_runs DEFAULT VALUES")
    run = conn.execute("SELECT status, finished_at, started_at FROM check_runs").fetchone()
    assert run["status"] == "running" and run["finished_at"] is None and run["started_at"]
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO check_runs (status) VALUES ('kacau')")

    conn.execute("INSERT INTO activity_logs (action, detail) VALUES ('published', 'x')")
    log = conn.execute("SELECT user_id, created_at FROM activity_logs").fetchone()
    assert log["user_id"] is None and log["created_at"]

    conn.execute("INSERT INTO users (id, telegram_id) VALUES (1, '123')")
    conn.execute("INSERT INTO activity_logs (user_id, action) VALUES (1, 'approved')")
    conn.execute("DELETE FROM users WHERE id = 1")  # log tetap ada, user_id jadi NULL
    assert conn.execute("SELECT COUNT(*) FROM activity_logs WHERE user_id IS NULL").fetchone()[0] == 2


def test_failed_migration_rolls_back(conn, tmp_path, monkeypatch):
    (tmp_path / "001_ok.sql").write_text("CREATE TABLE a (id INTEGER);")
    (tmp_path / "002_rusak.sql").write_text("CREATE TABLE b (id INTEGER); INSERT INTO tidak_ada VALUES (1);")
    monkeypatch.setattr(migrate, "MIGRATIONS_DIR", tmp_path)

    with pytest.raises(sqlite3.OperationalError):
        migrate.apply_migrations(conn)
    assert migrate.current_version(conn) == 1
    assert "a" in tables(conn) and "b" not in tables(conn)


def test_rejects_gap_in_numbering(tmp_path, monkeypatch):
    (tmp_path / "001_a.sql").write_text("")
    (tmp_path / "003_c.sql").write_text("")
    monkeypatch.setattr(migrate, "MIGRATIONS_DIR", tmp_path)
    with pytest.raises(RuntimeError):
        migrate.list_migrations()
