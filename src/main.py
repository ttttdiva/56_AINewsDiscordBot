from __future__ import annotations

import argparse
import logging
import sys
from typing import Sequence

from pydantic import ValidationError

from src.config.settings import AppSettings, RunMode, load_settings
from src.logging_config import configure_logging
from src.scheduler.daily_scheduler import DailyScheduler
from src.services.app_runner import AppRunner

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI News Discord Bot entrypoint.")
    parser.add_argument(
        "--mode",
        choices=[mode.value for mode in RunMode],
        help="Override the run mode from APP_MODE.",
    )
    return parser


def run(mode: RunMode, settings: AppSettings) -> int:
    runner = AppRunner(settings)

    logger.info(
        "Loaded configuration for mode=%s timezone=%s post_time=%s channel=%s",
        mode.value,
        settings.bot_timezone,
        settings.daily_post_time.strftime("%H:%M"),
        settings.discord_channel_id,
    )

    if mode is RunMode.SCHEDULE:
        scheduler = DailyScheduler(settings, runner)
        scheduler.start()
        return 0

    return runner.run_sync(mode)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        settings = load_settings()
    except ValidationError as exc:
        print("Configuration validation failed.", file=sys.stderr)
        print(exc, file=sys.stderr)
        return 2

    configure_logging(settings.log_level)
    mode = RunMode(args.mode) if args.mode else settings.app_mode
    return run(mode, settings)


if __name__ == "__main__":
    raise SystemExit(main())
