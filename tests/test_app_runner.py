from datetime import date

from src.config.settings import AppSettings
from src.services.app_runner import AppRunner


def test_resolve_digest_date_defaults_to_previous_day() -> None:
    runner = AppRunner(AppSettings())
    resolved = runner.resolve_digest_date(None, current_date=date(2026, 3, 12))

    assert resolved == date(2026, 3, 11)


def test_resolve_digest_date_uses_override() -> None:
    runner = AppRunner(AppSettings())

    assert runner.resolve_digest_date(date(2026, 3, 11)) == date(2026, 3, 11)
