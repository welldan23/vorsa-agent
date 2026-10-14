"""Tampilan rincian skor kepentingan berita dari AI."""

from dataclasses import dataclass
from html import escape

BAR_WIDTH = 10

# kriteria penilaian AI → label tampilan
CRITERIA_LABELS = {
    "impact": "Dampak ke pembaca",
    "novelty": "Kebaruan",
    "audience_fit": "Cocok untuk audiens VORSA",
    "virality": "Potensi ramai dibahas",
}


@dataclass(frozen=True)
class ScoreDetail:
    article_id: int
    title: str
    category: str
    score: float  # skor akhir 0–1
    threshold: float  # ambang lolos kategori (categories.min_relevance)
    criteria: dict[str, float]  # kunci CRITERIA_LABELS → 0–1
    reason: str | None

    @property
    def passed(self) -> bool:
        return self.score >= self.threshold


def score_bar(value: float) -> str:
    filled = round(max(0.0, min(1.0, value)) * BAR_WIDTH)
    return "█" * filled + "░" * (BAR_WIDTH - filled)


def render_score_detail(d: ScoreDetail) -> str:
    verdict = "✅ Lolos saring" if d.passed else "🚫 Tidak lolos saring"
    lines = [
        "<b>📊 Skor Kepentingan</b>",
        f"<i>{escape(d.title)}</i>",
        "",
        f"<code>{score_bar(d.score)}</code> <b>{d.score:.0%}</b>",
        f"{verdict} · ambang {escape(d.category)} {d.threshold:.0%}",
    ]
    if d.criteria:
        lines += ["", "<b>Rincian penilaian AI</b>"]
        for key, value in d.criteria.items():
            lines.append(f"<code>{score_bar(value)}</code> {value:.0%} {escape(CRITERIA_LABELS.get(key, key))}")
    if d.reason:
        lines += ["", f"💡 <i>{escape(d.reason)}</i>"]
    return "\n".join(lines)
