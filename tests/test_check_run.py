import asyncio

import pytest

from vorsa.config import Settings
from vorsa.scheduler import CHECK_JOB_ID, create_scheduler
from vorsa.services import check_run, fetcher
from vorsa.services.check_run import recover_interrupted_runs, run_check
from vorsa.services.fetcher import FeedEntry, FetchResult
from vorsa.services.monitoring import get_monitoring_status


def entry(n):
    return FeedEntry(title=f"Berita {n}", link=f"https://x.id/{n}", summary="", published_at=None)


@pytest.fixture
def seeded(db):
    db.executemany(
        "INSERT INTO categories (id, name, is_enabled) VALUES (?, ?, ?)",
        [(1, "Teknologi & AI", 1), (2, "Tren Internet", 0)],
    )
    db.executemany(
        "INSERT INTO rss_sources (id, category_id, url, is_active, last_error) VALUES (?, ?, ?, ?, ?)",
        [
            (1, 1, "https://ok/rss", 1, "error lama"),
            (2, 1, "https://mati/rss", 1, None),
            (3, 1, "https://nonaktif/rss", 0, None),
            (4, 2, "https://kategori-mati/rss", 1, None),
        ],
    )
    return db


def fake_fetch(monkeypatch, results_by_id, seen=None):
    async def fetch_all(sources, session=None):
        if seen is not None:
            seen.extend(sid for sid, _ in sources)
        return [results_by_id[sid] for sid, _ in sources]

    monkeypatch.setattr(fetcher, "fetch_all", fetch_all)


def run_row(db, run_id):
    return db.execute("SELECT * FROM check_runs WHERE id = ?", (run_id,)).fetchone()


def test_partial_run_records_everything(seeded, monkeypatch):
    seen = []
    fake_fetch(
        monkeypatch,
        {
            1: FetchResult(1, "https://ok/rss", entries=[entry(1), entry(2), entry(1)]),
            2: FetchResult(2, "https://mati/rss", error="HTTP 500"),
        },
        seen,
    )
    run_id = asyncio.run(run_check(seeded))

    assert seen == [1, 2]  # sumber nonaktif & kategori mati tidak diambil
    run = run_row(seeded, run_id)
    assert run["status"] == "partial" and run["finished_at"]
    assert (run["sources_checked"], run["sources_failed"], run["new_articles"], run["duplicates_skipped"]) == (
        2, 1, 2, 1,
    )
    ok, dead = seeded.execute("SELECT last_error, last_fetched_at FROM rss_sources WHERE id IN (1, 2) ORDER BY id")
    assert ok["last_error"] is None and ok["last_fetched_at"]  # error lama dihapus
    assert dead["last_error"] == "HTTP 500" and dead["last_fetched_at"] is None

    status = get_monitoring_status(seeded, 15)
    assert status.bot_active
    assert status.categories[0].failing_sources == 1 and status.categories[0].new_articles == 2


def test_all_sources_failing(seeded, monkeypatch):
    fake_fetch(
        monkeypatch,
        {1: FetchResult(1, "u", error="Timeout 10 detik"), 2: FetchResult(2, "u", error="HTTP 404")},
    )
    assert run_row(seeded, asyncio.run(run_check(seeded)))["status"] == "failed"


def test_no_sources_is_success(db, monkeypatch):
    fake_fetch(monkeypatch, {})
    run = run_row(db, asyncio.run(run_check(db)))
    assert run["status"] == "success" and run["sources_checked"] == 0


def test_unexpected_error_marks_run_failed(seeded, monkeypatch):
    async def boom(sources, session=None):
        raise RuntimeError("jaringan kacau")

    monkeypatch.setattr(fetcher, "fetch_all", boom)
    run = run_row(seeded, asyncio.run(run_check(seeded)))
    assert run["status"] == "failed" and "jaringan kacau" in run["error_message"]


def test_overlapping_runs_are_skipped(seeded, monkeypatch):
    async def slow(sources, session=None):
        await asyncio.sleep(0.05)
        return [FetchResult(sid, url) for sid, url in sources]

    monkeypatch.setattr(fetcher, "fetch_all", slow)
    monkeypatch.setattr(check_run, "_lock", None)  # lock baru di event loop tes

    async def both():
        check_run._lock = asyncio.Lock()
        return await asyncio.gather(run_check(seeded), run_check(seeded))

    first, second = asyncio.run(both())
    assert first is not None and second is None


def test_recover_interrupted_runs(db):
    db.execute("INSERT INTO check_runs DEFAULT VALUES")
    assert recover_interrupted_runs(db) == 1
    row = db.execute("SELECT status, finished_at, error_message FROM check_runs").fetchone()
    assert row["status"] == "failed" and row["finished_at"] and "Terhenti" in row["error_message"]
    assert recover_interrupted_runs(db) == 0


def test_scheduler_job(db):
    settings = Settings(bot_token="x", database_path=":memory:", check_interval_minutes=15)
    job = create_scheduler(db, settings).get_job(CHECK_JOB_ID)
    assert job.trigger.interval.total_seconds() == 15 * 60
    assert job.max_instances == 1 and job.coalesce
    assert job.args == (db,)
