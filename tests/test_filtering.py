from src.models.news import NewsPost
from src.services.filtering import NewsFilter


def test_filtering_removes_duplicates_and_sent_posts() -> None:
    posts = [
        NewsPost(
            rank=1,
            title="A",
            summary="summary a",
            post_id="1",
            post_url="https://x.com/test/status/1",
            content_excerpt="excerpt a",
        ),
        NewsPost(
            rank=2,
            title="B",
            summary="summary b",
            post_id="1",
            post_url="https://x.com/test/status/1",
            content_excerpt="excerpt b",
        ),
        NewsPost(
            rank=3,
            title="C",
            summary="summary c",
            post_id="3",
            post_url="https://x.com/test/status/3",
            content_excerpt="excerpt c",
        ),
    ]

    filtered = NewsFilter(max_items=5).filter_posts(posts, sent_source_keys={"3"})

    assert [post.title for post in filtered] == ["A"]
