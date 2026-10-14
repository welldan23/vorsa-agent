"""Service ringkasan Panel Utama: gabungan status pemantauan, berita, dan aktivitas."""

import sqlite3
from datetime import datetime

from vorsa.services.activity import get_last_activity
from vorsa.services.monitoring import get_monitoring_status
from vorsa.services.news import count_important_today
from vorsa.ui.activity import describe_activity
from vorsa.ui.panel import PanelSnapshot


def get_panel_snapshot(
    conn: sqlite3.Connection, interval_minutes: int, now: datetime | None = None
) -> PanelSnapshot:
    now = now or datetime.now()
    status = get_monitoring_status(conn, interval_minutes, now=now)
    last = get_last_activity(conn)
    return PanelSnapshot(
        bot_active=status.bot_active,
        last_checked_at=status.last_checked_at,
        active_categories=sum(c.enabled for c in status.categories),
        total_categories=len(status.categories),
        important_today=count_important_today(conn),
        pending_review=0,  # tabel designs baru ada di fase 2
        last_activity=describe_activity(last) if last else None,
        generated_at=now,
    )
