from datetime import date

from src.models.news import DigestDraft, NewsPost
from src.storage.sqlite_repository import SQLiteStateRepository


def test_repository_upserts_posts_and_digest(tmp_path) -> None:
    repo = SQLiteStateRepository(tmp_path / "state.db")
    repo.initialize()

    run_id = repo.start_run("manual")
    posts = [
        NewsPost(
            rank=1,
            title="A",
            summary="summary a",
            post_id="1",
            post_url="https://x.com/test/status/1",
            content_excerpt="excerpt a",
        )
    ]
    source_ids = repo.upsert_source_posts(run_id, posts)

    draft = DigestDraft(
        digest_date=date(2026, 3, 11),
        headline="AI",
        overview="overview",
        items=[],
        markdown="# AI",
    )
    digest_id = repo.save_digest(draft, 12345)
    repo.mark_digest_posted(digest_id, [111, 222])

    assert source_ids["1"] > 0
    digest = repo.get_digest_by_date(date(2026, 3, 11))
    assert digest is not None
    assert digest["status"] == "posted"
