import asyncio
from datetime import datetime, timezone

import aiohttp
import pytest
from aiohttp import web

from vorsa.services import fetcher
from vorsa.services.fetcher import FeedError, clean_text, fetch_all, parse_feed

RSS = b"""<?xml version="1.0"?>
<rss version="2.0"><channel><title>Contoh</title>
<item>
  <title>Harga emas &amp; perak naik</title>
  <link>https://contoh.id/emas</link>
  <description><![CDATA[<p>Harga <b>emas</b> tembus   rekor.</p><img src="x.jpg"/>]]></description>
  <pubDate>Tue, 14 Oct 2026 03:30:00 +0700</pubDate>
</item>
<item><title>Tanpa tanggal</title><link>https://contoh.id/b</link></item>
<item><title></title><link>https://contoh.id/tanpa-judul</link></item>
<item><title>Tanpa link</title></item>
</channel></rss>"""

ATOM = b"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"><title>Atom</title>
<entry><title>Model AI baru</title><link href="https://atom.test/ai"/>
<summary>Ringkas</summary><updated>2026-10-13T20:00:00Z</updated></entry>
</feed>"""


def test_parse_rss():
    first, second = parse_feed(RSS)
    assert first.title == "Harga emas & perak naik"
    assert first.link == "https://contoh.id/emas"
    assert first.summary == "Harga emas tembus rekor."
    assert first.published_at == datetime(2026, 10, 13, 20, 30, tzinfo=timezone.utc)
    assert second.published_at is None and second.summary == ""


def test_parse_atom():
    (entry,) = parse_feed(ATOM)
    assert (entry.title, entry.link, entry.summary) == ("Model AI baru", "https://atom.test/ai", "Ringkas")
    assert entry.published_at == datetime(2026, 10, 13, 20, 0, tzinfo=timezone.utc)


def test_parse_garbage():
    with pytest.raises(FeedError, match="Bukan feed"):
        parse_feed(b"<html><body>Halaman biasa</body></html>")


def test_clean_text_truncates():
    assert clean_text("a" * 10, max_chars=5) == "aaaa…"
    assert clean_text(None) == ""


async def _serve_and_fetch(monkeypatch, paths):
    monkeypatch.setattr(fetcher, "TIMEOUT_SECONDS", 0.5)

    async def ok(_):
        return web.Response(body=RSS, content_type="application/rss+xml")

    async def slow(_):
        await asyncio.sleep(2)
        return web.Response(body=RSS)

    async def html(_):
        return web.Response(text="<html>bukan feed</html>", content_type="text/html")

    app = web.Application()
    app.router.add_get("/ok", ok)
    app.router.add_get("/slow", slow)
    app.router.add_get("/html", html)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]
    try:
        async with aiohttp.ClientSession(trust_env=False) as session:
            sources = [(i, f"http://127.0.0.1:{port}{p}") for i, p in enumerate(paths, start=1)]
            return await fetch_all(sources, session=session)
    finally:
        await runner.cleanup()


def test_fetch_all_isolates_failures(monkeypatch):
    results = asyncio.run(_serve_and_fetch(monkeypatch, ["/ok", "/missing", "/slow", "/html"]))
    assert [r.source_id for r in results] == [1, 2, 3, 4]
    ok, missing, slow, html = results
    assert ok.ok and len(ok.entries) == 2
    assert missing.error == "HTTP 404"
    assert slow.error == "Timeout 0.5 detik"
    assert html.error == "Bukan feed RSS/Atom yang valid"


def test_fetch_all_unreachable_host():
    async def go():
        async with aiohttp.ClientSession(trust_env=False) as session:
            return await fetch_all([(1, "http://127.0.0.1:9/rss")], session=session)

    (result,) = asyncio.run(go())
    assert not result.ok and result.error.startswith("Gagal terhubung")


def test_valid_empty_feed_is_not_an_error():
    assert parse_feed(b'<?xml version="1.0"?><rss version="2.0"><channel><title>x</title></channel></rss>') == []
