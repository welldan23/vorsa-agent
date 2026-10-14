from datetime import datetime, timedelta

from vorsa.db.timeutil import to_db
from vorsa.services.activity import get_last_activity, get_recent_activity, log_activity


def test_empty(db):
    assert get_recent_activity(db) == []
    assert get_last_activity(db) is None


def test_log_and_read_newest_first(db):
    now = datetime.now().replace(microsecond=0)
    db.execute(
        "INSERT INTO activity_logs (action, detail, created_at) VALUES ('approved', 'lama', ?)",
        (to_db(now - timedelta(hours=1)),),
    )
    log_activity(db, "flagged", "“Harga emas”")
    log_activity(db, "design_created", "“Harga emas”")  # detik yang sama → urut id

    entries = get_recent_activity(db)
    assert [e.action for e in entries] == ["design_created", "flagged", "approved"]
    assert entries[2].created_at == now - timedelta(hours=1)
    assert abs(entries[0].created_at - datetime.now()) < timedelta(seconds=5)
    assert get_last_activity(db).action == "design_created"


def test_limit_and_user(db):
    db.execute("INSERT INTO users (id, telegram_id) VALUES (7, '123')")
    for i in range(15):
        log_activity(db, "published", f"#{i}", user_id=7)
    assert len(get_recent_activity(db)) == 10
    assert len(get_recent_activity(db, limit=3)) == 3
    assert db.execute("SELECT COUNT(*) FROM activity_logs WHERE user_id = 7").fetchone()[0] == 15
