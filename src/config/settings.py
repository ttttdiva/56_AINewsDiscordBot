from __future__ import annotations

from datetime import time
from enum import Enum
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from dotenv import dotenv_values
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]
LOCAL_ENV_PATH = ROOT_DIR / ".env"
DEFAULT_DISCORD_CHANNEL_ID = 1481265352032915506

_SETTINGS_CACHE: "AppSettings | None" = None


def _parse_handles(raw_value: str | list[str] | None) -> list[str]:
    if raw_value is None:
        return []
    if isinstance(raw_value, list):
        parts = raw_value
    else:
        parts = raw_value.replace("\uFF20", "@").split(",")

    handles: list[str] = []
    for part in parts:
        handle = part.strip()
        if not handle:
            continue
        if handle.startswith("@"):
            handle = handle[1:]
        if handle:
            handles.append(handle)
    return handles


def _blank_to_none(raw_value: object) -> object:
    if isinstance(raw_value, str) and not raw_value.strip():
        return None
    return raw_value


def _load_env_values() -> dict[str, str]:
    merged: dict[str, str] = {}
    if LOCAL_ENV_PATH.exists():
        values = dotenv_values(LOCAL_ENV_PATH)
        for key, value in values.items():
            if value is None or value == "":
                continue
            merged[key] = value

    if "Discord_TOKEN" in merged and "DISCORD_BOT_TOKEN" not in merged:
        merged["DISCORD_BOT_TOKEN"] = merged["Discord_TOKEN"]
    if "GROK_API_KEY" in merged and "XAI_API_KEY" not in merged:
        merged["XAI_API_KEY"] = merged["GROK_API_KEY"]
    return merged


class RunMode(str, Enum):
    DRY_RUN = "dry-run"
    MANUAL = "manual"
    SCHEDULE = "schedule"


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=None,
        case_sensitive=False,
        extra="ignore",
    )

    app_mode: RunMode = Field(default=RunMode.DRY_RUN, alias="APP_MODE")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    xai_api_key: str | None = Field(default=None, alias="XAI_API_KEY")
    xai_api_base: str = Field(default="https://api.x.ai/v1", alias="XAI_API_BASE")
    xai_grok_model: str = Field(default="grok-4-0709", alias="XAI_GROK_MODEL")
    grok_timeout_seconds: int = Field(default=180, alias="GROK_TIMEOUT_SECONDS")

    discord_bot_token: str | None = Field(default=None, alias="DISCORD_BOT_TOKEN")
    discord_channel_id: int = Field(default=DEFAULT_DISCORD_CHANNEL_ID, alias="DISCORD_CHANNEL_ID")

    bot_timezone: str = Field(default="Asia/Tokyo", alias="BOT_TIMEZONE")
    daily_post_time: time = Field(default=time(8, 0), alias="DAILY_POST_TIME")

    ai_news_query: str = Field(
        default='(AI OR "artificial intelligence" OR LLM OR "large language model" OR OpenAI OR Anthropic OR Gemini OR Claude OR Grok) (launch OR released OR funding OR paper OR benchmark OR model OR agent OR policy)',
        alias="AI_NEWS_QUERY",
    )
    allowed_x_handles: list[str] = Field(default_factory=list, alias="ALLOWED_X_HANDLES")
    excluded_x_handles: list[str] = Field(default_factory=list, alias="EXCLUDED_X_HANDLES")
    x_search_max_results: int = Field(default=8, alias="X_SEARCH_MAX_RESULTS")
    x_search_language: str = Field(default="ja", alias="X_SEARCH_LANGUAGE")
    search_lookback_days: int = Field(default=1, alias="SEARCH_LOOKBACK_DAYS")
    digest_max_items: int = Field(default=5, alias="DIGEST_MAX_ITEMS")

    state_db_path: Path = Field(default=Path("data/state.db"), alias="STATE_DB_PATH")
    raw_output_dir: Path = Field(default=Path("data/raw"), alias="RAW_OUTPUT_DIR")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        normalized = value.upper()
        if normalized not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {sorted(allowed)}")
        return normalized

    @field_validator("daily_post_time", mode="before")
    @classmethod
    def validate_daily_post_time(cls, value: str | time) -> time:
        if isinstance(value, time):
            return value

        parts = value.split(":")
        if len(parts) != 2:
            raise ValueError("DAILY_POST_TIME must be HH:MM")

        try:
            hour = int(parts[0])
            minute = int(parts[1])
        except ValueError as exc:
            raise ValueError("DAILY_POST_TIME must be HH:MM") from exc

        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("DAILY_POST_TIME must be a valid 24-hour time")
        return time(hour=hour, minute=minute)

    @field_validator("bot_timezone")
    @classmethod
    def validate_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"Unknown timezone: {value}") from exc
        return value

    @field_validator("allowed_x_handles", "excluded_x_handles", mode="before")
    @classmethod
    def parse_handles(cls, value: str | list[str] | None) -> list[str]:
        return _parse_handles(value)

    @field_validator("xai_api_key", "discord_bot_token", mode="before")
    @classmethod
    def blank_optional_values_to_none(cls, value: object) -> object:
        return _blank_to_none(value)

    @field_validator("discord_channel_id")
    @classmethod
    def validate_channel_id(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("DISCORD_CHANNEL_ID must be a positive integer")
        return value

    @field_validator("x_search_max_results", "grok_timeout_seconds", "search_lookback_days", "digest_max_items")
    @classmethod
    def validate_positive_int(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Value must be a positive integer")
        return value

    @property
    def timezone(self) -> ZoneInfo:
        return ZoneInfo(self.bot_timezone)

    @property
    def state_db_abspath(self) -> Path:
        if self.state_db_path.is_absolute():
            return self.state_db_path
        return (ROOT_DIR / self.state_db_path).resolve()

    @property
    def raw_output_dir_abspath(self) -> Path:
        if self.raw_output_dir.is_absolute():
            return self.raw_output_dir
        return (ROOT_DIR / self.raw_output_dir).resolve()

    def ensure_runtime_dirs(self) -> None:
        self.state_db_abspath.parent.mkdir(parents=True, exist_ok=True)
        self.raw_output_dir_abspath.mkdir(parents=True, exist_ok=True)


def load_settings(force_reload: bool = False) -> AppSettings:
    global _SETTINGS_CACHE
    if force_reload or _SETTINGS_CACHE is None:
        explicit_values: dict[str, Any] = _load_env_values()
        _SETTINGS_CACHE = AppSettings(**explicit_values)
    return _SETTINGS_CACHE
