import asyncio
from dataclasses import replace

from vorsa.stub.samples import sample_score_detail
from vorsa.ui.score import render_score_detail, score_bar


def test_score_bar():
    assert score_bar(0.91) == "█████████░"
    assert score_bar(0) == "░" * 10 and score_bar(1.4) == "█" * 10


def test_render_passed_and_failed():
    d = sample_score_detail()
    text = render_score_detail(d)
    assert "<b>91%</b>" in text and "✅ Lolos saring · ambang Ekonomi &amp; Bisnis 70%" in text
    assert "95% Dampak ke pembaca" in text and "88% Potensi ramai dibahas" in text

    low = render_score_detail(replace(d, score=0.55, criteria={}, reason=None))
    assert "🚫 Tidak lolos saring" in low and "Rincian" not in low and "💡" not in low


def test_score_button_round_trip(tg):
    asyncio.run(tg.press("art:score:0"))
    asyncio.run(tg.press("art:card:0"))
    score, card = tg.texts()
    assert "📊 Skor Kepentingan" in score
    assert "🔔 <b>Berita Penting</b>" in card
