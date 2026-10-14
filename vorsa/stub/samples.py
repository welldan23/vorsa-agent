"""Contoh data untuk tampilan yang backend-nya belum ada (fase 2)."""

import io
import textwrap
from dataclasses import replace
from datetime import datetime, timedelta

from PIL import Image, ImageDraw, ImageFont

from vorsa.ui.design import DesignDraft
from vorsa.ui.notification import ArticleNotification
from vorsa.ui.score import ScoreDetail


_flagged: set[int] = set()  # status tandai berita contoh selama bot jalan


def set_sample_flag(flagged: bool) -> None:
    (_flagged.add if flagged else _flagged.discard)(0)


def sample_notification() -> ArticleNotification:
    return _sample_notification() if 0 not in _flagged else replace(_sample_notification(), is_flagged=True)


def _sample_notification() -> ArticleNotification:
    return ArticleNotification(
        id=0,
        title="Harga emas tembus rekor baru, investor ramai beralih ke logam mulia",
        category="Ekonomi & Bisnis",
        source="cnbcindonesia.com",
        link="https://www.cnbcindonesia.com/market",
        summary=(
            "Harga emas dunia menembus level tertinggi sepanjang masa setelah bank sentral "
            "memberi sinyal pemangkasan suku bunga. Permintaan emas batangan di dalam negeri ikut melonjak."
        ),
        relevance_score=0.91,
        reason="Berdampak langsung ke keuangan pembaca dan sedang ramai dibahas.",
        published_at=datetime.now() - timedelta(minutes=12),
    )


def sample_score_detail() -> ScoreDetail:
    n = sample_notification()
    return ScoreDetail(
        article_id=n.id,
        title=n.title,
        category=n.category,
        score=n.relevance_score,
        threshold=0.70,
        criteria={"impact": 0.95, "novelty": 0.85, "audience_fit": 0.9, "virality": 0.88},
        reason=n.reason,
    )


def sample_design() -> DesignDraft:
    n = _sample_notification()
    return DesignDraft(
        id=0,
        article_id=n.id,
        article_title=n.title,
        category=n.category,
        version=1,
        status="draft",
        headline="EMAS PECAH REKOR. SAATNYA IKUT BELI?",
        caption=(
            "Harga emas dunia baru aja tembus rekor tertinggi sepanjang masa 🟡\n\n"
            "Pemicunya: sinyal bank sentral bakal pangkas suku bunga. Di dalam negeri, "
            "antrean beli emas batangan juga makin panjang.\n\n"
            "Kamu tim nabung emas atau tim nunggu turun? Tulis di komentar 👇"
        ),
        hashtags=["VORSA", "emas", "ekonomi", "investasi"],
        created_at=datetime.now(),
    )


def sample_design_image(headline: str) -> bytes:
    """Gambar pengganti 1080x1350 (rasio feed Instagram) sampai renderer VORSA asli ada."""
    img = Image.new("RGB", (1080, 1350), "#111111")
    draw = ImageDraw.Draw(img)
    draw.rectangle((60, 60, 1020, 1290), outline="#F5C400", width=6)
    draw.text((100, 110), "VORSA", fill="#F5C400", font=ImageFont.load_default(56))
    y = 520
    for line in textwrap.wrap(headline, width=16):
        draw.text((100, y), line, fill="white", font=ImageFont.load_default(84))
        y += 100
    draw.text((100, 1190), "PRATINJAU CONTOH", fill="#888888", font=ImageFont.load_default(36))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
