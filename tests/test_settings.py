from pydantic import ValidationError

from src.config.settings import AppSettings


def test_settings_parse_handles_and_time() -> None:
    settings = AppSettings(
        ALLOWED_X_HANDLES="@OpenAI, @xai,\uFF20AnthropicAI",
        EXCLUDED_X_HANDLES="spam_account",
        DAILY_POST_TIME="7:05",
    )

    assert settings.allowed_x_handles == ["OpenAI", "xai", "AnthropicAI"]
    assert settings.excluded_x_handles == ["spam_account"]
    assert settings.daily_post_time.strftime("%H:%M") == "07:05"


def test_settings_validate_timezone() -> None:
    try:
        AppSettings(BOT_TIMEZONE="Invalid/Timezone")
    except ValidationError:
        pass
    else:
        raise AssertionError("Expected invalid timezone to fail validation")
