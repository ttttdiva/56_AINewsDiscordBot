from src.bot.discord_publisher import split_message


def test_split_message_respects_limit() -> None:
    content = "A" * 1990 + "\n\n" + "B" * 100

    chunks = split_message(content, limit=2000)

    assert len(chunks) == 2
    assert len(chunks[0]) <= 2000
    assert len(chunks[1]) <= 2000
