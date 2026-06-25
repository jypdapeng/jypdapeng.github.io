"""定时任务调度。"""

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.services.daily_pipeline import run_daily_collection

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


def start_scheduler() -> None:
    """启动每日采集调度。"""
    scheduler.add_job(
        _run_job,
        trigger="cron",
        hour=settings.daily_collect_hour,
        minute=settings.daily_collect_minute,
        id="daily_collect",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        "Daily collector scheduled at %02d:%02d UTC",
        settings.daily_collect_hour,
        settings.daily_collect_minute,
    )


async def _run_job() -> None:
    """调度任务包装。"""
    try:
        report = await run_daily_collection()
        logger.info("Daily report generated for %s", report["report_date"])
    except Exception:  # noqa: BLE001
        logger.exception("Daily collection failed")
