from __future__ import annotations

from src.models.news import NewsPost

LOW_SIGNAL_KEYWORDS = (
    "giveaway",
    "follow me",
    "airdrop",
    "gm",
    "good morning",
    "join my discord",
)


class NewsFilter:
    def __init__(self, max_items: int) -> None:
        self._max_items = max_items

    def filter_posts(self, posts: list[NewsPost], sent_source_keys: set[str]) -> list[NewsPost]:
        selected: list[NewsPost] = []
        seen: set[str] = set()

        for post in sorted(posts, key=self._sort_key):
            key = post.source_key
            if key in seen or key in sent_source_keys:
                continue
            if self._looks_low_signal(post):
                continue
            seen.add(key)
            selected.append(post)
            if len(selected) >= self._max_items:
                break

        return selected

    @staticmethod
    def _sort_key(post: NewsPost) -> tuple[int, str]:
        rank = post.rank if post.rank is not None else 9999
        timestamp = post.posted_at.isoformat() if post.posted_at else ""
        return rank, timestamp

    @staticmethod
    def _looks_low_signal(post: NewsPost) -> bool:
        haystack = f"{post.title}\n{post.summary}\n{post.content_excerpt}".lower()
        return any(keyword in haystack for keyword in LOW_SIGNAL_KEYWORDS)
