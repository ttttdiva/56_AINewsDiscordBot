from src.prompts.loader import load_prompt_template, render_prompt_template


def test_load_prompt_template_reads_prompt_file() -> None:
    template = load_prompt_template("news_collection_system.txt")

    assert "AI news editor" in template
    assert "strict JSON" in template


def test_render_prompt_template_formats_values() -> None:
    rendered = render_prompt_template(
        "news_collection_user.txt",
        from_date="2026-03-10",
        to_date="2026-03-11",
        query="OpenAI",
        language="ja",
        candidate_count=5,
        allowed_handles="none",
        excluded_handles="none",
    )

    assert "Time window start (inclusive): 2026-03-10" in rendered
    assert "Time window end (exclusive): 2026-03-11" in rendered
    assert "Target query: OpenAI" in rendered
