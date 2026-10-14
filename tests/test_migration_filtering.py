import sqlite3

import pytest


def seed(db):
    db.execute("INSERT INTO categories (id, name) VALUES (1, 'Teknologi & AI')")
    db.execute("INSERT INTO rss_sources (id, category_id, url) VALUES (1, 1, 'https://a/rss')")
    db.execute("INSERT INTO users (id, telegram_id) VALUES (1, '111')")
    db.execute(
        "INSERT INTO articles (id, source_id, category_id, title, link, content_hash) VALUES (1, 1, 1, 'A', 'l', 'h')"
    )


def test_article_filter_columns_default_to_unscored(db):
    seed(db)
    row = db.execute(
        "SELECT relevance_reason, relevance_criteria, scored_at, notified_at, is_ignored FROM articles"
    ).fetchone()
    assert tuple(row) == (None, None, None, None, 0)
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("UPDATE articles SET is_ignored = 2")


def test_unscored_queue_uses_partial_index(db):
    seed(db)
    plan = " ".join(
        r[3] for r in db.execute("EXPLAIN QUERY PLAN SELECT id FROM articles WHERE scored_at IS NULL ORDER BY fetched_at")
    )
    assert "idx_articles_unscored" in plan


def test_notifications_unique_per_user_and_cascade(db):
    seed(db)
    db.execute("INSERT INTO notifications (article_id, user_id, chat_id, message_id) VALUES (1, 1, 111, 5)")
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO notifications (article_id, user_id, chat_id, message_id) VALUES (1, 1, 111, 6)")
    db.execute("DELETE FROM articles")
    assert db.execute("SELECT COUNT(*) FROM notifications").fetchone()[0] == 0
