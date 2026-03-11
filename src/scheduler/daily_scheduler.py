from __future__ import annotations

import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from src.config.settings import AppSettings, RunMode
from src.services.app_runner import AppRunner

logger = logging.getLogger(__name__)


class DailyScheduler:
    def __init__(self, settings: AppSettings, runner: AppRunner) -> None:
        self._settings = settings
        self._runner = runner

    def start(self) -> None:
        scheduler = BlockingScheduler(timezone=self._settings.bot_timezone)
        trigger = CronTrigger(
            hour=self._settings.daily_post_time.hour,
            minute=self._settings.daily_post_time.minute,
            timezone=self._settings.bot_timezone,
        )
        scheduler.add_job(
            self._runner.run_sync,
            trigger=trigger,
            args=[RunMode.SCHEDULE],
            id="daily_ai_news_digest",
            max_instances=1,
            coalesce=True,
            replace_existing=True,
        )

        logger.info(
            "Scheduler started. Daily run at %s %s",
            self._settings.bot_timezone,
            self._settings.daily_post_time.strftime("%H:%M"),
        )
        scheduler.start()
