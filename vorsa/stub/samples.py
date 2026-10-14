"""Contoh data untuk tampilan yang backend-nya belum ada (fase 2)."""

from datetime import datetime, timedelta

from vorsa.ui.notification import ArticleNotification


def sample_notification() -> ArticleNotification:
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
