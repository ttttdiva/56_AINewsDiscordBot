from datetime import date

from src.models.news import EventDecision, NewsPost
from src.services.summarizer import DigestBuilder


def test_digest_builder_formats_daily_digest_without_section_headers() -> None:
    draft = DigestBuilder().build(
        date(2026, 3, 12),
        "bad title from model",
        "overview that should not appear",
        [
            NewsPost(
                rank=1,
                title="OpenAIが新モデルを公開",
                summary="推論性能を改善した新モデルを発表した。",
                selection_reason="主要プレイヤーの新リリースだから",
                post_id="1",
                post_url="https://x.com/openai/status/1",
                author_handle="@OpenAI",
                content_excerpt="excerpt",
                dedupe_decision=EventDecision.EVENT_UPDATE,
                new_facts=["提供開始時期が明示された"],
            )
        ],
    )

    assert draft.headline == "3/12 AIニュース"
    assert draft.markdown.startswith("# 3/12 AIニュース")
    assert "## 概要" not in draft.markdown
    assert "## トピック" not in draft.markdown
    assert "日付:" not in draft.markdown
    assert "1. OpenAIが新モデルを公開" in draft.markdown
    assert "X: https://x.com/openai/status/1" in draft.markdown
    assert "ポイント: 主要プレイヤーの新リリースだから" in draft.markdown
    assert "続報: 新情報があるため採用" in draft.markdown
