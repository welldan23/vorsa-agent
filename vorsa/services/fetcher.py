"""Ambil dan parsing feed RSS/Atom.

Modul ini tidak menyentuh database: hasilnya diserahkan ke deduplikasi/penyimpanan.
Satu sumber yang gagal tidak menggagalkan sumber lain.
"""

import asyncio
import calendar
import html
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

import aiohttp
import feedparser

log = logging.getLogger(__name__)

TIMEOUT_SECONDS = 10
MAX_CONCURRENT = 5  # ringan untuk VPS kecil
MAX_FEED_BYTES = 5 * 1024 * 1024
SUMMARY_MAX_CHARS = 500
USER_AGENT = "VORSA-Bot/1.0 (+RSS reader)"

_TAG = re.compile(r"<[^>]+>")
_SPACE = re.compile(r"\s+")


@dataclass(frozen=True)
class FeedEntry:
    title: str
    link: str
    summary: str
    published_at: datetime | None  # UTC, None kalau feed tidak mencantumkan


@dataclass(frozen=True)
class FetchResult:
    source_id: int
    url: str
    entries: list[FeedEntry] = field(default_factory=list)
    error: str | None = None  # pesan ramah untuk ditampilkan; None = berhasil

    @property
    def ok(self) -> bool:
        return self.error is None


class FeedError(Exception):
    """Feed tidak bisa diambil/dibaca; pesannya siap ditampilkan ke pengguna."""


def clean_text(raw: str | None, max_chars: int | None = None) -> str:
    text = _SPACE.sub(" ", html.unescape(_TAG.sub(" ", raw or ""))).strip()
    if max_chars and len(text) > max_chars:
        text = text[: max_chars - 1].rstrip() + "…"
    return text


def _published(entry) -> datetime | None:
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if not parsed:
        return None
    return datetime.fromtimestamp(calendar.timegm(parsed), tz=timezone.utc)


def parse_feed(content: bytes) -> list[FeedEntry]:
    """Bytes RSS/Atom → daftar entri. Entri tanpa judul atau link dilewati."""
    feed = feedparser.parse(content)
    # version kosong = dokumen tidak dikenali sebagai RSS/Atom (mis. halaman HTML biasa).
    if not feed.version and not feed.entries:
        raise FeedError("Bukan feed RSS/Atom yang valid")

    entries = []
    for item in feed.entries:
        title = clean_text(item.get("title"))
        link = (item.get("link") or "").strip()
        if not title or not link:
            continue
        summary = clean_text(item.get("summary") or item.get("description"), SUMMARY_MAX_CHARS)
        entries.append(FeedEntry(title=title, link=link, summary=summary, published_at=_published(item)))
    return entries


async def fetch_feed(session: aiohttp.ClientSession, url: str) -> list[FeedEntry]:
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=TIMEOUT_SECONDS)) as resp:
            if resp.status != 200:
                raise FeedError(f"HTTP {resp.status}")
            content = await resp.content.read(MAX_FEED_BYTES + 1)
    except asyncio.TimeoutError as err:
        raise FeedError(f"Timeout {TIMEOUT_SECONDS} detik") from err
    except aiohttp.ClientError as err:
        raise FeedError(f"Gagal terhubung ({type(err).__name__})") from err
    if len(content) > MAX_FEED_BYTES:
        raise FeedError("Feed terlalu besar")
    # feedparser sinkron; jalankan di thread supaya bot tidak tersendat.
    return await asyncio.to_thread(parse_feed, content)


def new_session() -> aiohttp.ClientSession:
    # trust_env: ikuti HTTPS_PROXY kalau server memakainya.
    return aiohttp.ClientSession(headers={"User-Agent": USER_AGENT}, trust_env=True)


async def fetch_all(
    sources: list[tuple[int, str]], session: aiohttp.ClientSession | None = None
) -> list[FetchResult]:
    """Ambil banyak sumber (id, url) sekaligus; hasil urut sama dengan input."""
    own_session = session is None
    session = session or new_session()
    limit = asyncio.Semaphore(MAX_CONCURRENT)

    async def one(source_id: int, url: str) -> FetchResult:
        async with limit:
            try:
                return FetchResult(source_id, url, entries=await fetch_feed(session, url))
            except FeedError as err:
                log.warning("Sumber %s gagal: %s", url, err)
                return FetchResult(source_id, url, error=str(err))
            except Exception:  # sumber aneh tidak boleh menjatuhkan seluruh putaran
                log.exception("Error tak terduga saat mengambil %s", url)
                return FetchResult(source_id, url, error="Error tak terduga")

    try:
        return await asyncio.gather(*(one(sid, url) for sid, url in sources))
    finally:
        if own_session:
            await session.close()
