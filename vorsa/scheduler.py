"""Penjadwal pemantauan RSS (APScheduler)."""

import sqlite3
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from vorsa.config import Settings
from vorsa.services.check_run import run_check

CHECK_JOB_ID = "rss_check"


def create_scheduler(db: sqlite3.Connection, settings: Settings) -> AsyncIOScheduler:
    """Jadwal cek RSS tiap N menit; putaran pertama langsung saat bot menyala."""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_check,
        "interval",
        minutes=settings.check_interval_minutes,
        args=[db],
        id=CHECK_JOB_ID,
        next_run_time=datetime.now(),
        max_instances=1,  # jangan tumpuk putaran
        coalesce=True,  # putaran yang terlewat (mis. server sibuk) digabung jadi satu
        misfire_grace_time=60,
    )
    return scheduler
