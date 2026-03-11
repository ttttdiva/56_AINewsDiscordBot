from __future__ import annotations

from datetime import date

from src.models.news import DigestDraft, DigestItem, NewsPost


class DigestBuilder:
    def build(self, digest_date: date, headline: str, overview: str, posts: list[NewsPost]) -> DigestDraft:
        display_headline = self._build_headline(digest_date)
        items = [
            DigestItem(
                rank_order=index,
                title=post.title,
                summary=post.summary,
                post_url=post.post_url,
                author_handle=post.author_handle,
                selection_reason=post.selection_reason,
                posted_at=post.posted_at,
                source=post,
            )
            for index, post in enumerate(posts, start=1)
        ]
        markdown = self._build_markdown(digest_date, display_headline, overview, items)
        return DigestDraft(
            digest_date=digest_date,
            headline=display_headline,
            overview=overview,
            items=items,
            markdown=markdown,
        )

    def _build_markdown(self, digest_date: date, headline: str, overview: str, items: list[DigestItem]) -> str:
        lines = [f"# {headline}", ""]

        if not items:
            lines.extend(
                [
                    "本日の条件では、新規の主要 AI ニュースは見つかりませんでした。",
                ]
            )
            return "\n".join(lines).strip()

        for item in items:
            lines.extend(
                [
                    f"{item.rank_order}. {item.title}",
                    item.summary.strip(),
                    f"X: {item.post_url}" if item.post_url else "X: unavailable",
                ]
            )
            if item.author_handle:
                lines.append(f"投稿元: {item.author_handle}")
            if item.selection_reason:
                lines.append(f"ポイント: {item.selection_reason}")
            if item.source.dedupe_decision.value == "event_update":
                lines.append("続報: 新情報があるため採用")
                if item.source.new_facts:
                    lines.append(f"新情報: {' / '.join(item.source.new_facts)}")
            lines.append("")

        return "\n".join(lines).strip()

    @staticmethod
    def _build_headline(digest_date: date) -> str:
        return f"{digest_date.month}/{digest_date.day} AIニュース"
