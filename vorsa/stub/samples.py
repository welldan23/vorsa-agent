"""Contoh data untuk tampilan yang backend-nya belum ada (fase 2)."""

from dataclasses import replace
from datetime import datetime, timedelta

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
