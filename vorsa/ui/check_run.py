"""Tampilan teks laporan pengecekan RSS terakhir."""

from dataclasses import dataclass
from datetime import datetime
from html import escape

from vorsa.ui.sources import short_url


@dataclass(frozen=True)
class SourceFailure:
    url: str
    category: str
    error: str


@dataclass(frozen=True)
class CheckRun:
    started_at: datetime
    finished_at: datetime | None  # None = masih berjalan
    next_check_at: datetime | None
    interval_minutes: int
    sources_checked: int
    failures: list[SourceFailure]
    new_articles: int
    duplicates_skipped: int
    passed_filter: int
    new_per_category: dict[str, int]
    error: str | None = None  # alasan kalau putaran gagal total


def render_check_in_progress(source_count: int) -> str:
    return f"<b>🧾 Pengecekan Terakhir</b>\n\n⏳ Sedang mengecek {source_count} sumber… tunggu sebentar ya."


def render_check_run(run: CheckRun | None) -> str:
    lines = ["<b>🧾 Pengecekan Terakhir</b>", ""]
    if run is None:
        lines.append("Belum ada pengecekan. Pengecekan pertama jalan otomatis setelah bot menyala.")
        return "\n".join(lines)

    if run.finished_at is None:
        lines.append(f"Mulai {run.started_at:%H:%M} · ⏳ sedang berjalan…")
        return "\n".join(lines)
    if run.error:
        lines += [f"Mulai {run.started_at:%H:%M} · ❌ gagal total", f"<i>{escape(run.error)}</i>"]
        return "\n".join(lines)

    seconds = round((run.finished_at - run.started_at).total_seconds())
    ok = run.sources_checked - len(run.failures)
    next_check = f"{run.next_check_at:%H:%M}" if run.next_check_at else "—"
    sources = f"Sumber dicek: {run.sources_checked} · ✅ {ok} berhasil"
    if run.failures:
        sources += f" · ⚠️ {len(run.failures)} gagal"

    lines += [
        f"Mulai {run.started_at:%H:%M} · selesai dalam {seconds} detik",
        f"Berikutnya {next_check} (otomatis tiap {run.interval_minutes} menit)",
        "",
        sources,
        f"📥 {run.new_articles} berita baru",
        f"🔁 {run.duplicates_skipped} berita kembar dibuang",
        f"⭐ {run.passed_filter} lolos saring",
    ]
    if run.new_per_category:
        lines += ["", "<b>Berita baru per kategori</b>"]
        lines += [f"• {escape(name)}: {count}" for name, count in run.new_per_category.items()]
    if run.failures:
        lines += ["", "<b>Sumber gagal</b>"]
        lines += [
            f"⚠️ {escape(short_url(f.url))} ({escape(f.category)}) — {escape(f.error)}"
            for f in run.failures
        ]
        lines += ["", "<i>Sumber yang gagal dilewati; sumber lain tetap diproses.</i>"]
    return "\n".join(lines)
