"""Buang berita kembar lalu simpan berita baru ke tabel articles.

Berita dianggap kembar kalau link-nya sama (setelah dinormalkan) ATAU judulnya sama
(setelah dinormalkan, disimpan sebagai content_hash). Keduanya UNIQUE di database,
jadi duplikat cukup diabaikan dengan INSERT OR IGNORE.
"""

import hashlib
import re
import sqlite3
import unicodedata
from collections import Counter
from dataclasses import dataclass
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from vorsa.db.timeutil import to_db
from vorsa.services.fetcher import FeedEntry

_TRACKING_PARAMS = {"fbclid", "gclid", "igshid", "mc_cid", "mc_eid", "ref", "ref_src"}
_NON_WORD = re.compile(r"[^\w]+")


@dataclass(frozen=True)
class StoreResult:
    new: int
    duplicates: int


def normalize_link(url: str) -> str:
    """Samakan link yang beda tampilan tapi menunjuk berita yang sama."""
    parts = urlsplit(url.strip())
    host = parts.netloc.lower().removeprefix("www.")
    query = urlencode(
        [
            (k, v)
            for k, v in parse_qsl(parts.query, keep_blank_values=True)
            if not k.lower().startswith("utm_") and k.lower() not in _TRACKING_PARAMS
        ]
    )
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower() or "https", host, path, query, ""))


def normalize_title(title: str) -> str:
    text = unicodedata.normalize("NFKC", title).casefold()
    return _NON_WORD.sub(" ", text).strip()


def content_hash(title: str) -> str:
    return hashlib.sha256(normalize_title(title).encode()).hexdigest()


# Satu link dipakai sebanyak ini judul berbeda dalam satu feed → bukan link berita.
# (2 judul untuk 1 link masih wajar: berita yang judulnya diperbarui.)
SHARED_LINK_TITLES = 3


def _article_links(entries: list[FeedEntry]) -> list[str]:
    """Link per entri. Ada feed (mis. Google Trends) yang memberi link SAMA untuk semua
    entrinya, atau hanya link halaman depan; link seperti itu bukan identitas berita,
    jadi dibuat unik per judul (deduplikasi lalu bergantung pada judul)."""
    links = [normalize_link(e.link) for e in entries]
    distinct_titles = Counter(link for link, _ in {(l, content_hash(e.title)) for l, e in zip(links, entries)})

    def is_identity(link: str) -> bool:
        return distinct_titles[link] < SHARED_LINK_TITLES and urlsplit(link).path != "/"

    return [
        link if is_identity(link) else f"{link}#{content_hash(e.title)[:12]}"
        for link, e in zip(links, entries)
    ]


def store_entries(
    conn: sqlite3.Connection, source_id: int, category_id: int, entries: list[FeedEntry]
) -> StoreResult:
    """Simpan entri yang belum pernah ada; mengembalikan jumlah baru & kembar."""
    new = 0
    with conn:
        for entry, link in zip(entries, _article_links(entries)):
            cur = conn.execute(
                """
                INSERT OR IGNORE INTO articles
                    (source_id, category_id, title, link, summary, content_hash, published_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    source_id,
                    category_id,
                    entry.title,
                    link,
                    entry.summary,
                    content_hash(entry.title),
                    to_db(entry.published_at) if entry.published_at else None,
                ),
            )
            new += cur.rowcount
    return StoreResult(new=new, duplicates=len(entries) - new)
