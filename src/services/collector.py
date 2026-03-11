from __future__ import annotations

import logging
import re
from datetime import date, datetime, timedelta
from typing import Any

from src.clients.grok_client import GrokClient, extract_json_object
from src.config.settings import AppSettings
from src.models.news import CollectionResult, NewsPost

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are an AI news editor for a Discord digest.
Use x_search to find high-signal AI-related news on X.
Focus on product launches, model releases, benchmarks, funding, policy, research, outages, and major partnerships.
Ignore memes, engagement bait, giveaways, reposts, and low-signal promotion unless the event is materially important.
Return strict JSON only.
Schema:
{
  "headline": "string",
  "overview": "2-4 short Japanese sentences",
  "items": [
    {
      "rank": 1,
      "title": "short Japanese headline",
      "summary": "1-2 short Japanese sentences",
      "selection_reason": "why it matters in Japanese",
      "post_id": "string or null",
      "post_url": "full X status URL",
      "author_handle": "@handle or null",
      "posted_at": "ISO-8601 datetime or null",
      "content_excerpt": "short excerpt from the source post"
    }
  ]
}
Do not wrap JSON in markdown fences.
Every item must include a direct X status URL.
""".strip()


class NewsCollector:
    def __init__(self, settings: AppSettings, grok_client: GrokClient) -> None:
        self._settings = settings
        self._grok_client = grok_client

    async def collect(self, digest_date: date) -> CollectionResult:
        from_date = digest_date - timedelta(days=self._settings.search_lookback_days)
        to_date = digest_date + timedelta(days=1)

        candidate_count = max(
            self._settings.digest_max_items,
            min(self._settings.x_search_max_results, self._settings.digest_max_items + 1),
        )
        user_prompt = self._build_user_prompt(from_date, to_date, candidate_count)
        raw_payload, raw_text = await self._grok_client.search_ai_news(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            from_date=from_date.isoformat(),
            to_date=to_date.isoformat(),
        )
        parsed = extract_json_object(raw_text)

        items = self._normalize_items(parsed.get("items"), raw_payload)
        headline = self._clean_string(parsed.get("headline")) or f"{digest_date.isoformat()} AI News Digest"
        overview = self._clean_string(parsed.get("overview")) or self._fallback_overview(items)

        return CollectionResult(
            headline=headline,
            overview=overview,
            items=items,
            raw_response_text=raw_text,
            raw_response_payload=raw_payload,
            query=self._settings.ai_news_query,
            from_date=from_date,
            to_date=to_date,
        )

    def _build_user_prompt(self, from_date: date, to_date: date, candidate_count: int) -> str:
        allowed_handles = ", ".join(f"@{handle}" for handle in self._settings.allowed_x_handles) or "none"
        excluded_handles = ", ".join(f"@{handle}" for handle in self._settings.excluded_x_handles) or "none"
        return (
            f"Search for recent AI news on X.\n"
            f"Time window: {from_date.isoformat()} to {to_date.isoformat()}.\n"
            f"Target query: {self._settings.ai_news_query}\n"
            f"Preferred summary language: {self._settings.x_search_language}\n"
            f"Return {candidate_count} items or fewer, ranked by importance.\n"
            f"Allowed handles: {allowed_handles}\n"
            f"Excluded handles: {excluded_handles}\n"
            "Prioritize concrete news developments over opinions.\n"
        )

    def _normalize_items(self, raw_items: Any, raw_payload: dict[str, Any]) -> list[NewsPost]:
        if not isinstance(raw_items, list):
            return []

        citation_urls = self._extract_citation_urls(raw_payload)
        items: list[NewsPost] = []
        for index, raw_item in enumerate(raw_items, start=1):
            if not isinstance(raw_item, dict):
                continue
            url = self._clean_string(
                raw_item.get("post_url") or raw_item.get("url") or raw_item.get("source_url")
            )
            if not url and index - 1 < len(citation_urls):
                url = citation_urls[index - 1]
            if not url:
                continue

            post_id = self._clean_string(raw_item.get("post_id")) or self._extract_post_id(url)
            title = self._clean_string(raw_item.get("title")) or f"AI News Item {index}"
            summary = self._clean_string(raw_item.get("summary")) or self._clean_string(raw_item.get("content_excerpt"))
            excerpt = self._clean_string(raw_item.get("content_excerpt")) or summary
            if not summary or not excerpt:
                continue

            posted_at = self._parse_datetime(self._clean_string(raw_item.get("posted_at")))
            author_handle = self._clean_handle(raw_item.get("author_handle"))
            selection_reason = self._clean_string(raw_item.get("selection_reason"))

            try:
                item = NewsPost(
                    rank=self._parse_rank(raw_item.get("rank"), index),
                    title=title,
                    summary=summary,
                    selection_reason=selection_reason,
                    post_id=post_id,
                    post_url=url,
                    author_handle=author_handle,
                    posted_at=posted_at,
                    content_excerpt=excerpt,
                    raw_payload=raw_item,
                )
            except Exception as exc:  # pragma: no cover
                logger.warning("Skipping invalid item from Grok response: %s", exc)
                continue

            items.append(item)

        items.sort(key=lambda item: item.rank or 9999)
        return items

    def _extract_citation_urls(self, payload: dict[str, Any]) -> list[str]:
        urls: list[str] = []
        outputs = payload.get("output")
        if not isinstance(outputs, list):
            return urls

        for output in outputs:
            if not isinstance(output, dict) or output.get("type") != "message":
                continue
            content = output.get("content")
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict):
                    continue
                annotations = block.get("annotations")
                if not isinstance(annotations, list):
                    continue
                for annotation in annotations:
                    if isinstance(annotation, dict) and annotation.get("type") == "url_citation":
                        url = self._clean_string(annotation.get("url"))
                        if url and url not in urls:
                            urls.append(url)
        return urls

    @staticmethod
    def _clean_string(value: Any) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            value = str(value)
        cleaned = value.strip()
        return cleaned or None

    @staticmethod
    def _clean_handle(value: Any) -> str | None:
        handle = NewsCollector._clean_string(value)
        if not handle:
            return None
        if not handle.startswith("@"):
            handle = f"@{handle}"
        return handle

    @staticmethod
    def _parse_rank(value: Any, default: int) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _extract_post_id(url: str) -> str | None:
        match = re.search(r"/status/(\d+)", url)
        return match.group(1) if match else None

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    @staticmethod
    def _fallback_overview(items: list[NewsPost]) -> str:
        if not items:
            return "直近 1 日で重複を除いて残る主要な AI ニュースは見つかりませんでした。"
        summaries = [item.summary for item in items[:3]]
        return " ".join(summaries)
