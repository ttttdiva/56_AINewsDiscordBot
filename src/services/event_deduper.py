from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date

from src.clients.grok_client import GrokClient, extract_json_object
from src.models.news import EventDeduplicationResult, EventDecision, HistoricalNewsItem, NewsPost
from src.prompts.loader import load_prompt_template, render_prompt_template


@dataclass
class EventDeduplicationOutcome:
    kept_posts: list[NewsPost]
    results: list[EventDeduplicationResult]


class EventDeduper:
    def __init__(self, grok_client: GrokClient, lookback_days: int) -> None:
        self._grok_client = grok_client
        self._lookback_days = lookback_days

    async def dedupe_against_history(
        self,
        *,
        today_posts: list[NewsPost],
        historical_items: list[HistoricalNewsItem],
    ) -> EventDeduplicationOutcome:
        if not today_posts:
            return EventDeduplicationOutcome(kept_posts=[], results=[])

        if not historical_items:
            results = [
                EventDeduplicationResult(
                    today_post_url=post.post_url,
                    decision=EventDecision.NEW_EVENT,
                    confidence=1.0,
                    reason="No posted items were found in the lookback window.",
                    new_facts=[],
                )
                for post in today_posts
                if post.post_url is not None
            ]
            return EventDeduplicationOutcome(kept_posts=today_posts, results=results)

        system_prompt = load_prompt_template("news_dedupe_system.txt")
        user_prompt = render_prompt_template(
            "news_dedupe_user.txt",
            lookback_days=self._lookback_days,
            today_items_json=json.dumps(self._serialize_today_items(today_posts), ensure_ascii=False, indent=2),
            past_items_json=json.dumps(self._serialize_historical_items(historical_items), ensure_ascii=False, indent=2),
        )
        _, raw_text = await self._grok_client.create_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_output_tokens=1800,
        )
        parsed = extract_json_object(raw_text)
        results = self._parse_results(parsed.get("results"))
        result_by_url = {str(result.today_post_url): result for result in results}

        kept_posts: list[NewsPost] = []
        for post in today_posts:
            if post.post_url is None:
                kept_posts.append(post)
                continue

            result = result_by_url.get(str(post.post_url))
            if result is None:
                post.dedupe_decision = EventDecision.NEW_EVENT
                post.dedupe_reason = "No explicit decision returned by dedupe classifier; defaulted to new_event."
                post.dedupe_confidence = 0.5
                kept_posts.append(post)
                continue

            post.dedupe_decision = result.decision
            post.dedupe_reason = result.reason
            post.dedupe_confidence = result.confidence
            post.matched_past_post_url = result.matched_past_post_url
            post.matched_past_digest_date = result.matched_past_digest_date
            post.new_facts = list(result.new_facts)

            if result.decision is not EventDecision.DUPLICATE_EVENT:
                kept_posts.append(post)

        return EventDeduplicationOutcome(kept_posts=kept_posts, results=results)

    @staticmethod
    def _serialize_today_items(posts: list[NewsPost]) -> list[dict[str, object]]:
        serialized: list[dict[str, object]] = []
        for post in posts:
            serialized.append(
                {
                    "title": post.title,
                    "summary": post.summary,
                    "selection_reason": post.selection_reason,
                    "post_id": post.post_id,
                    "post_url": str(post.post_url) if post.post_url else None,
                    "author_handle": post.author_handle,
                    "content_excerpt": post.content_excerpt,
                }
            )
        return serialized

    @staticmethod
    def _serialize_historical_items(items: list[HistoricalNewsItem]) -> list[dict[str, object]]:
        serialized: list[dict[str, object]] = []
        for item in items:
            serialized.append(
                {
                    "digest_date": item.digest_date.isoformat(),
                    "title": item.title,
                    "summary": item.summary,
                    "selection_reason": item.selection_reason,
                    "post_id": item.post_id,
                    "post_url": str(item.post_url) if item.post_url else None,
                    "author_handle": item.author_handle,
                    "content_excerpt": item.content_excerpt,
                }
            )
        return serialized

    @staticmethod
    def _parse_results(raw_results: object) -> list[EventDeduplicationResult]:
        if not isinstance(raw_results, list):
            return []
        parsed: list[EventDeduplicationResult] = []
        for raw_result in raw_results:
            if not isinstance(raw_result, dict):
                continue
            try:
                parsed.append(EventDeduplicationResult(**raw_result))
            except Exception:
                continue
        return parsed
