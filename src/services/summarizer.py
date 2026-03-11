from __future__ import annotations

from datetime import date

from src.models.news import DigestDraft, DigestItem, NewsPost


class DigestBuilder:
    def build(self, digest_date: date, headline: str, overview: str, posts: list[NewsPost]) -> DigestDraft:
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
        markdown = self._build_markdown(digest_date, headline, overview, items)
        return DigestDraft(
            digest_date=digest_date,
            headline=headline,
            overview=overview,
            items=items,
            markdown=markdown,
        )

    def _build_markdown(self, digest_date: date, headline: str, overview: str, items: list[DigestItem]) -> str:
        lines = [
            f"# {headline}",
            f"日付: {digest_date.isoformat()}",
            "",
            "## 概要",
            overview.strip(),
            "",
        ]

        if not items:
            lines.extend(
                [
                    "## トピック",
                    "本日の条件では、新規の主要 AI ニュースは見つかりませんでした。",
                ]
            )
            return "\n".join(lines).strip()

        lines.append("## トピック")
        for item in items:
            lines.extend(
                [
                    f"### {item.rank_order}. {item.title}",
                    item.summary.strip(),
                    f"Source: {item.post_url}" if item.post_url else "Source: unavailable",
                ]
            )
            if item.author_handle:
                lines.append(f"Handle: {item.author_handle}")
            if item.selection_reason:
                lines.append(f"Why it matters: {item.selection_reason}")
            if item.source.dedupe_decision.value == "event_update":
                lines.append("Update: 続報として採用")
                if item.source.new_facts:
                    lines.append(f"New facts: {' / '.join(item.source.new_facts)}")
            lines.append("")

        return "\n".join(lines).strip()
