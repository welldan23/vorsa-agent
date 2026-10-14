"""Buang berita kembar lalu simpan berita baru ke tabel articles.

Berita dianggap kembar kalau link-nya sama (setelah dinormalkan) ATAU judulnya sama
(setelah dinormalkan, disimpan sebagai content_hash). Keduanya UNIQUE di database,
jadi duplikat cukup diabaikan dengan INSERT OR IGNORE.
"""

import hashlib
import re
import sqlite3
import unicodedata
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


def store_entries(
    conn: sqlite3.Connection, source_id: int, category_id: int, entries: list[FeedEntry]
) -> StoreResult:
    """Simpan entri yang belum pernah ada; mengembalikan jumlah baru & kembar."""
    new = 0
    with conn:
        for entry in entries:
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
                    normalize_link(entry.link),
                    entry.summary,
                    content_hash(entry.title),
                    to_db(entry.published_at) if entry.published_at else None,
                ),
            )
            new += cur.rowcount
    return StoreResult(new=new, duplicates=len(entries) - new)
