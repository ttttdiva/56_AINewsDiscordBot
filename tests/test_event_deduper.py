import asyncio
from datetime import date

from src.models.news import EventDecision, HistoricalNewsItem, NewsPost
from src.services.event_deduper import EventDeduper


class FakeGrokClient:
    def __init__(self, text: str) -> None:
        self._text = text

    async def create_response(self, **kwargs):  # type: ignore[no-untyped-def]
        return {}, self._text


def test_event_deduper_filters_duplicates_and_keeps_updates() -> None:
    today_posts = [
        NewsPost(
            rank=1,
            title="NemoClaw announced",
            summary="NVIDIA plans NemoClaw.",
            post_url="https://x.com/a/status/1",
            content_excerpt="NVIDIA plans NemoClaw.",
        ),
        NewsPost(
            rank=2,
            title="BitNet open sourced",
            summary="Microsoft open sourced BitNet.",
            post_url="https://x.com/a/status/2",
            content_excerpt="Microsoft open sourced BitNet.",
        ),
    ]
    history = [
        HistoricalNewsItem(
            digest_date=date(2026, 3, 10),
            source_post_id=10,
            title="NemoClaw planned",
            summary="NVIDIA plans NemoClaw.",
            post_url="https://x.com/old/status/10",
            content_excerpt="NVIDIA plans NemoClaw.",
        )
    ]
    response = """
    {
      "results": [
        {
          "today_post_url": "https://x.com/a/status/1",
          "decision": "duplicate_event",
          "matched_past_post_url": "https://x.com/old/status/10",
          "matched_past_digest_date": "2026-03-10",
          "confidence": 0.98,
          "reason": "Same event.",
          "new_facts": []
        },
        {
          "today_post_url": "https://x.com/a/status/2",
          "decision": "event_update",
          "matched_past_post_url": "https://x.com/old/status/10",
          "matched_past_digest_date": "2026-03-10",
          "confidence": 0.84,
          "reason": "Adds new facts.",
          "new_facts": ["Open sourced on GitHub"]
        }
      ]
    }
    """

    outcome = asyncio.run(
        EventDeduper(FakeGrokClient(response), lookback_days=7).dedupe_against_history(
            today_posts=today_posts,
            historical_items=history,
        )
    )

    assert [post.title for post in outcome.kept_posts] == ["BitNet open sourced"]
    assert outcome.kept_posts[0].dedupe_decision is EventDecision.EVENT_UPDATE
    assert outcome.kept_posts[0].new_facts == ["Open sourced on GitHub"]
