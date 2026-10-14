"""Data tiruan untuk Panel Utama selama backend belum ada.

Bentuk datanya sudah mengikuti kontrak yang nanti diisi backend
(scheduler, tabel articles, activity_logs).
"""

from datetime import datetime, timedelta

from vorsa.ui.activity import ActivityEntry, describe_activity
from vorsa.ui.categories import CategoryItem
from vorsa.ui.check_run import CheckRun, SourceFailure
from vorsa.ui.monitor import MonitorOverview
from vorsa.ui.news import ArticleSummary
from vorsa.ui.panel import PanelSnapshot
from vorsa.ui.sources import RssSourceItem
from vorsa.ui.status import CategoryStatus, MonitoringStatus


# State tiruan di memori: perubahan (toggle kategori, tambah/hapus sumber) bertahan selama bot jalan.
# id → [nama, aktif, ambang relevansi, berita baru pada cek terakhir]
_CATEGORIES: dict[int, list] = {
    1: ["Teknologi & AI", True, 0.70, 3],
    2: ["Ekonomi & Bisnis", True, 0.70, 2],
    3: ["Berita Nasional", True, 0.75, 4],
    4: ["Culture & Entertainment", True, 0.65, 1],
    5: ["Berita Internasional", True, 0.75, 2],
    6: ["Musik & Lifestyle", True, 0.60, 0],
    7: ["Tren Internet", True, 0.60, 1],
}

# (kategori, url, aktif, gagal pada cek terakhir)
_SOURCE_ROWS = [
    (1, "https://www.theverge.com/rss/index.xml", True, False),
    (1, "https://techcrunch.com/feed/", True, False),
    (1, "https://inet.detik.com/rss", True, False),
    (2, "https://www.cnbcindonesia.com/news/rss", True, False),
    (2, "https://ekonomi.bisnis.com/rss", True, False),
    (3, "https://www.kompas.com/rss", True, False),
    (3, "https://www.antaranews.com/rss/terkini.xml", True, True),
    (3, "https://nasional.tempo.co/rss", False, False),
    (4, "https://hot.detik.com/rss", True, False),
    (5, "https://feeds.reuters.com/reuters/worldNews", True, False),
    (5, "https://feeds.bbci.co.uk/news/world/rss.xml", True, False),
    (6, "https://www.rollingstone.com/music/feed/", True, False),
    (7, "https://trends.google.com/trending/rss?geo=ID", True, False),
]
_SOURCES: dict[int, dict] = {
    sid: {"category_id": cid, "url": url, "is_active": active, "failing": failing}
    for sid, (cid, url, active, failing) in enumerate(_SOURCE_ROWS, start=1)
}
_LAST_CHECK = datetime.now() - timedelta(minutes=6)


def _active_sources(category_id: int) -> list[dict]:
    return [s for s in _SOURCES.values() if s["category_id"] == category_id and s["is_active"]]


def get_categories() -> list[CategoryItem]:
    return [
        CategoryItem(
            id=cid,
            name=name,
            enabled=enabled,
            min_relevance=min_rel,
            source_count=len(_active_sources(cid)),
        )
        for cid, (name, enabled, min_rel, _) in _CATEGORIES.items()
    ]


def toggle_category(category_id: int) -> CategoryItem | None:
    row = _CATEGORIES.get(category_id)
    if row is None:
        return None
    row[1] = not row[1]
    return next(c for c in get_categories() if c.id == category_id)


def get_category(category_id: int) -> CategoryItem | None:
    return next((c for c in get_categories() if c.id == category_id), None)


def get_sources(category_id: int) -> list[RssSourceItem]:
    return [
        RssSourceItem(
            id=sid,
            category_id=s["category_id"],
            url=s["url"],
            is_active=s["is_active"],
            failing=s["failing"],
            last_fetched_at=_LAST_CHECK if s["is_active"] else None,
        )
        for sid, s in _SOURCES.items()
        if s["category_id"] == category_id
    ]


def get_source(source_id: int) -> RssSourceItem | None:
    s = _SOURCES.get(source_id)
    if s is None:
        return None
    return next(x for x in get_sources(s["category_id"]) if x.id == source_id)


def add_source(category_id: int, url: str) -> RssSourceItem | None:
    """Tambah sumber; None kalau URL sudah terdaftar (url unik di rss_sources)."""
    if any(s["url"] == url for s in _SOURCES.values()):
        return None
    sid = max(_SOURCES, default=0) + 1
    _SOURCES[sid] = {"category_id": category_id, "url": url, "is_active": True, "failing": False}
    return get_source(sid)


def delete_source(source_id: int) -> RssSourceItem | None:
    source = get_source(source_id)
    if source is not None:
        del _SOURCES[source_id]
    return source


def get_panel_snapshot() -> PanelSnapshot:
    now = datetime.now()
    status = get_monitoring_status()
    return PanelSnapshot(
        bot_active=status.bot_active,
        last_checked_at=status.last_checked_at,
        active_categories=sum(c.enabled for c in status.categories),
        total_categories=len(status.categories),
        important_today=len(get_important_articles()),
        pending_review=1,
        last_activity=describe_activity(get_recent_activity()[0]),
        generated_at=now,
    )


def get_important_articles() -> list[ArticleSummary]:
    now = datetime.now()
    rows = [
        ("Harga emas tembus rekor baru, investor ramai beralih", "Ekonomi & Bisnis", "CNBC Indonesia", 0.91, 12),
        ("OpenAI rilis model baru untuk agen otomatis", "Teknologi & AI", "The Verge", 0.88, 35),
        ("DPR sahkan RUU Perlindungan Data turunan", "Berita Nasional", "Kompas", 0.79, 58),
        ("Tur konser band Korea tambah jadwal di Jakarta", "Musik & Lifestyle", "Kumparan", 0.72, 95),
        ("Tren 'quiet vacation' ramai di TikTok", "Tren Internet", "Detik", 0.68, 140),
        ("KTT iklim sepakati dana transisi energi", "Berita Internasional", "Reuters", 0.74, 190),
    ]
    return [
        ArticleSummary(
            title=title,
            category=category,
            source=source,
            link=f"https://example.com/berita/{i}",
            relevance_score=score,
            published_at=now - timedelta(minutes=minutes_ago),
        )
        for i, (title, category, source, score, minutes_ago) in enumerate(rows, start=1)
    ]


def get_monitoring_status() -> MonitoringStatus:
    return MonitoringStatus(
        bot_active=True,
        interval_minutes=15,
        last_checked_at=_LAST_CHECK,
        next_check_at=_LAST_CHECK + timedelta(minutes=15),
        categories=[
            CategoryStatus(
                name=name,
                enabled=enabled,
                active_sources=len(_active_sources(cid)),
                failing_sources=sum(s["failing"] for s in _active_sources(cid)),
                new_articles=new,
            )
            for cid, (name, enabled, _, new) in _CATEGORIES.items()
        ],
    )


def get_recent_activity() -> list[ActivityEntry]:
    now = datetime.now()
    rows = [
        ("design_created", "“Harga emas tembus rekor baru”", 8),
        ("flagged", "“Harga emas tembus rekor baru”", 11),
        ("published", "“Startup lokal raih pendanaan Seri B”", 95),
        ("approved", "“Startup lokal raih pendanaan Seri B”", 97),
        ("design_revised", "“Startup lokal raih pendanaan Seri B” (v2)", 110),
        ("rejected", "“Gosip artis viral pekan ini”", 60 * 20),
        ("published", "“Bank sentral tahan suku bunga”", 60 * 26),
    ]
    return [
        ActivityEntry(action=action, detail=detail, created_at=now - timedelta(minutes=minutes_ago))
        for action, detail, minutes_ago in rows
    ]


def get_monitor_overview() -> MonitorOverview:
    status = get_monitoring_status()
    enabled = [c for c in status.categories if c.enabled]
    return MonitorOverview(
        running=status.bot_active,
        interval_minutes=status.interval_minutes,
        last_checked_at=status.last_checked_at,
        next_check_at=status.next_check_at,
        active_categories=len(enabled),
        total_categories=len(status.categories),
        active_sources=sum(c.active_sources for c in enabled),
        failing_sources=sum(c.failing_sources for c in enabled),
        fetched_today=148,
        duplicates_skipped_today=37,
        important_today=len(get_important_articles()),
    )


def get_last_check_run() -> CheckRun:
    status = get_monitoring_status()
    enabled = {cid for cid, row in _CATEGORIES.items() if row[1]}
    checked = [s for s in _SOURCES.values() if s["is_active"] and s["category_id"] in enabled]
    failures = [
        SourceFailure(url=s["url"], category=_CATEGORIES[s["category_id"]][0], error="Timeout 10 detik")
        for s in checked
        if s["failing"]
    ]
    per_category = {c.name: c.new_articles for c in status.categories if c.enabled}
    return CheckRun(
        started_at=_LAST_CHECK,
        finished_at=_LAST_CHECK + timedelta(seconds=23),
        next_check_at=status.next_check_at,
        interval_minutes=status.interval_minutes,
        sources_checked=len(checked),
        failures=failures,
        new_articles=sum(per_category.values()),
        duplicates_skipped=5,
        passed_filter=2,
        new_per_category=per_category,
    )
