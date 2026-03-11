from __future__ import annotations

from datetime import date, datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RunStatus(str, Enum):
    STARTED = "started"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class DigestStatus(str, Enum):
    PENDING = "pending"
    POSTED = "posted"
    FAILED = "failed"


class EventDecision(str, Enum):
    NEW_EVENT = "new_event"
    DUPLICATE_EVENT = "duplicate_event"
    EVENT_UPDATE = "event_update"


class NewsPost(BaseModel):
    rank: int | None = Field(default=None, ge=1)
    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    selection_reason: str | None = None
    post_id: str | None = None
    post_url: HttpUrl | None = None
    author_handle: str | None = None
    posted_at: datetime | None = None
    content_excerpt: str = Field(min_length=1)
    collected_at: datetime = Field(default_factory=utcnow)
    dedupe_decision: EventDecision = EventDecision.NEW_EVENT
    dedupe_reason: str | None = None
    dedupe_confidence: float | None = None
    matched_past_post_url: HttpUrl | None = None
    matched_past_digest_date: date | None = None
    new_facts: list[str] = Field(default_factory=list)
    raw_payload: dict[str, Any] = Field(default_factory=dict)

    @property
    def normalized_handle(self) -> str | None:
        if not self.author_handle:
            return None
        return self.author_handle.lstrip("@")

    @property
    def source_key(self) -> str:
        if self.post_id:
            return self.post_id
        if self.post_url:
            return str(self.post_url)
        return f"{self.title}|{self.summary}"


class DigestItem(BaseModel):
    rank_order: int = Field(ge=1)
    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    post_url: HttpUrl | None = None
    author_handle: str | None = None
    selection_reason: str | None = None
    posted_at: datetime | None = None
    source: NewsPost


class DigestDraft(BaseModel):
    digest_date: date
    headline: str = Field(min_length=1)
    overview: str = Field(min_length=1)
    items: list[DigestItem] = Field(default_factory=list)
    markdown: str = Field(min_length=1)
    created_at: datetime = Field(default_factory=utcnow)


class DeliveryRecord(BaseModel):
    digest_date: date
    discord_channel_id: int
    status: DigestStatus = DigestStatus.PENDING
    discord_message_ids: list[int] = Field(default_factory=list)
    posted_at: datetime | None = None
    failure_reason: str | None = None


class CollectionResult(BaseModel):
    headline: str = Field(min_length=1)
    overview: str = Field(min_length=1)
    items: list[NewsPost] = Field(default_factory=list)
    raw_response_text: str = Field(min_length=1)
    raw_response_payload: dict[str, Any] = Field(default_factory=dict)
    query: str = Field(min_length=1)
    from_date: date
    to_date: date
    collected_at: datetime = Field(default_factory=utcnow)


class RunRecord(BaseModel):
    id: int | None = None
    run_type: str = Field(min_length=1)
    status: RunStatus = RunStatus.STARTED
    started_at: datetime = Field(default_factory=utcnow)
    finished_at: datetime | None = None
    error_message: str | None = None


class HistoricalNewsItem(BaseModel):
    digest_date: date
    source_post_id: int
    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    selection_reason: str | None = None
    post_id: str | None = None
    post_url: HttpUrl | None = None
    author_handle: str | None = None
    content_excerpt: str = Field(min_length=1)


class EventDeduplicationResult(BaseModel):
    today_post_url: HttpUrl
    decision: EventDecision
    matched_past_post_url: HttpUrl | None = None
    matched_past_digest_date: date | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str = Field(min_length=1)
    new_facts: list[str] = Field(default_factory=list)
