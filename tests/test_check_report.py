import asyncio
from datetime import datetime, timedelta

import pytest

from vorsa.db.timeutil import to_db
from vorsa.services import check_run, fetcher
from vorsa.services.check_report import get_last_check_report, get_monitor_overview
from vorsa.services.fetcher import FeedEntry, FetchResult
from vorsa.ui.check_run import render_check_run


def run(coro):
    return asyncio.run(coro)


@pytest.fixture
def seeded(db):
    db.executemany(
        "INSERT INTO categories (id, name, is_enabled) VALUES (?, ?, ?)",
        [(1, "Teknologi & AI", 1), (2, "Tren Internet", 0)],
    )
    db.executemany(
        "INSERT INTO rss_sources (id, category_id, url) VALUES (?, ?, ?)",
        [(1, 1, "https://ok.id/rss"), (2, 1, "https://mati.id/rss"), (3, 2, "https://off.id/rss")],
    )
    return db


@pytest.fixture
def feeds(monkeypatch):
    async def fetch_all(sources, session=None):
        out = []
        for sid, url in sources:
            if "mati" in url:
                out.append(FetchResult(sid, url, error="HTTP 503"))
            else:
                entries = [FeedEntry(f"Berita {i}", f"https://ok.id/{i}", "", None) for i in range(3)]
                out.append(FetchResult(sid, url, entries=entries + entries[:1]))
        return out

    monkeypatch.setattr(fetcher, "fetch_all", fetch_all)


def test_no_report_before_first_check(seeded):
    assert get_last_check_report(seeded, 15) is None


def test_report_after_check(seeded, feeds):
    run(check_run.run_check(seeded))
    report = get_last_check_report(seeded, 15)
    assert (report.sources_checked, report.new_articles, report.duplicates_skipped) == (2, 3, 1)
    assert [(f.url, f.category, f.error) for f in report.failures] == [
        ("https://mati.id/rss", "Teknologi & AI", "HTTP 503")
    ]
    assert report.new_per_category == {"Teknologi & AI": 3}
    assert report.next_check_at is not None and report.error is None

    text = render_check_run(report)
    assert "Sumber dicek: 2 · ✅ 1 berhasil · ⚠️ 1 gagal" in text
    assert "📥 3 berita baru" in text and "🔁 1 berita kembar dibuang" in text
    assert "mati.id/rss (Teknologi &amp; AI) — HTTP 503" in text


def test_report_running_and_total_failure(seeded):
    seeded.execute("INSERT INTO check_runs DEFAULT VALUES")
    assert "⏳ sedang berjalan" in render_check_run(get_last_check_report(seeded, 15))

    check_run.recover_interrupted_runs(seeded)
    text = render_check_run(get_last_check_report(seeded, 15))
    assert "❌ gagal total" in text and "Terhenti" in text


def test_overview_counts_today_only(seeded, feeds):
    yesterday = to_db(datetime.now() - timedelta(days=1, hours=1))
    seeded.execute(
        "INSERT INTO check_runs (started_at, finished_at, status, duplicates_skipped) VALUES (?, ?, 'success', 50)",
        (yesterday, yesterday),
    )
    seeded.execute(
        "INSERT INTO articles (source_id, category_id, title, link, content_hash, fetched_at)"
        " VALUES (1, 1, 'lama', 'https://ok.id/lama', 'lama', ?)",
        (yesterday,),
    )
    run(check_run.run_check(seeded))

    o = get_monitor_overview(seeded, 15)
    assert o.running and o.interval_minutes == 15
    assert (o.active_categories, o.total_categories) == (1, 2)
    assert (o.active_sources, o.failing_sources) == (2, 1)
    assert (o.fetched_today, o.duplicates_skipped_today, o.important_today) == (3, 1, 0)


def test_hub_and_last_check_buttons(seeded, feeds, tg):
    run(check_run.run_check(seeded))
    run(tg.press("panel:monitor"))
    run(tg.press("mon:last_check"))
    hub, report = tg.texts()
    assert "🔗 Sumber RSS: 2 aktif · ⚠️ 1 gagal" in hub
    assert "📥 3 berita diambil" in hub
    assert "🧾 Pengecekan Terakhir" in report and "⚠️ 1 gagal" in report


def test_check_now_button(seeded, feeds, tg):
    run(tg.press("mon:check_now"))
    toast = next(c for c in tg.calls if type(c).__name__ == "AnswerCallbackQuery")
    assert toast.text == "⏱ Mulai mengecek…"
    progress, report = tg.texts()
    assert "⏳ Sedang mengecek 2 sumber" in progress
    assert "📥 3 berita baru" in report
    assert seeded.execute("SELECT COUNT(*) FROM check_runs").fetchone()[0] == 1


def test_check_now_while_another_check_runs(seeded, tg, monkeypatch):
    from vorsa.handlers import monitor

    monkeypatch.setattr(monitor, "is_check_running", lambda: True)
    run(tg.press("mon:check_now"))
    (call,) = tg.calls
    assert "sedang berjalan" in call.text and call.show_alert
    assert seeded.execute("SELECT COUNT(*) FROM check_runs").fetchone()[0] == 0
