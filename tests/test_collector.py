import asyncio
from datetime import date

from src.config.settings import AppSettings
from src.services.collector import NewsCollector


class FakeGrokClient:
    def __init__(self) -> None:
        self.calls: list[dict[str, str]] = []

    async def search_ai_news(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        from_date: str,
        to_date: str,
    ) -> tuple[dict, str]:
        self.calls.append(
            {
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "from_date": from_date,
                "to_date": to_date,
            }
        )
        return {}, '{"headline":"AIニュースダイジェスト 2026年3月11-13","overview":"overview","items":[]}'


def test_collector_uses_same_day_window_when_lookback_is_one() -> None:
    settings = AppSettings(SEARCH_LOOKBACK_DAYS="1")
    grok_client = FakeGrokClient()
    collector = NewsCollector(settings, grok_client)

    collection = asyncio.run(collector.collect(date(2026, 3, 12)))

    assert collection.from_date == date(2026, 3, 12)
    assert collection.to_date == date(2026, 3, 13)
    assert grok_client.calls[0]["from_date"] == "2026-03-12"
    assert grok_client.calls[0]["to_date"] == "2026-03-13"


def test_collector_uses_inclusive_lookback_window() -> None:
    settings = AppSettings(SEARCH_LOOKBACK_DAYS="3")
    grok_client = FakeGrokClient()
    collector = NewsCollector(settings, grok_client)

    collection = asyncio.run(collector.collect(date(2026, 3, 12)))

    assert collection.from_date == date(2026, 3, 10)
    assert collection.to_date == date(2026, 3, 13)
