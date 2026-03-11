from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from src.models.news import DigestDraft, DigestStatus, RunStatus


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SQLiteStateRepository:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def initialize(self) -> None:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
                PRAGMA journal_mode=WAL;

                CREATE TABLE IF NOT EXISTS bot_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_type TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    finished_at TEXT,
                    status TEXT NOT NULL,
                    error_message TEXT
                );

                CREATE TABLE IF NOT EXISTS source_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER,
                    post_id TEXT,
                    post_url TEXT,
                    author_handle TEXT,
                    posted_at TEXT,
                    title TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    selection_reason TEXT,
                    content_excerpt TEXT NOT NULL,
                    collected_at TEXT NOT NULL,
                    raw_rank INTEGER,
                    UNIQUE(post_id),
                    UNIQUE(post_url)
                );

                CREATE TABLE IF NOT EXISTS digest_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    digest_date TEXT NOT NULL UNIQUE,
                    headline TEXT NOT NULL,
                    overview TEXT NOT NULL,
                    summary_markdown TEXT NOT NULL,
                    discord_channel_id TEXT NOT NULL,
                    discord_message_ids TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    posted_at TEXT,
                    failure_reason TEXT
                );

                CREATE TABLE IF NOT EXISTS digest_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    digest_message_id INTEGER NOT NULL,
                    source_post_id INTEGER NOT NULL,
                    rank_order INTEGER NOT NULL,
                    selection_reason TEXT,
                    UNIQUE(digest_message_id, source_post_id)
                );
                """
            )

    def start_run(self, run_type: str) -> int:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO bot_runs (run_type, started_at, status)
                VALUES (?, ?, ?)
                """,
                (run_type, utcnow_iso(), RunStatus.STARTED.value),
            )
            return int(cursor.lastrowid)

    def finish_run(self, run_id: int, status: RunStatus, error_message: str | None = None) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE bot_runs
                SET finished_at = ?, status = ?, error_message = ?
                WHERE id = ?
                """,
                (utcnow_iso(), status.value, error_message, run_id),
            )

    def get_posted_source_keys(self) -> set[str]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT DISTINCT sp.post_id, sp.post_url
                FROM source_posts sp
                INNER JOIN digest_items di ON di.source_post_id = sp.id
                INNER JOIN digest_messages dm ON dm.id = di.digest_message_id
                WHERE dm.status = ?
                """,
                (DigestStatus.POSTED.value,),
            ).fetchall()

        keys: set[str] = set()
        for row in rows:
            if row["post_id"]:
                keys.add(row["post_id"])
            elif row["post_url"]:
                keys.add(row["post_url"])
        return keys

    def get_digest_by_date(self, digest_date: date) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM digest_messages
                WHERE digest_date = ?
                """,
                (digest_date.isoformat(),),
            ).fetchone()
        return dict(row) if row else None

    def upsert_source_posts(self, run_id: int, posts: list[Any]) -> dict[str, int]:
        source_post_ids: dict[str, int] = {}
        with self._connect() as connection:
            for post in posts:
                source_post_id = self._find_source_post_id(connection, post.post_id, str(post.post_url) if post.post_url else None)
                values = (
                    run_id,
                    post.post_id,
                    str(post.post_url) if post.post_url else None,
                    post.author_handle,
                    post.posted_at.isoformat() if post.posted_at else None,
                    post.title,
                    post.summary,
                    post.selection_reason,
                    post.content_excerpt,
                    post.collected_at.isoformat(),
                    post.rank,
                )
                if source_post_id is None:
                    cursor = connection.execute(
                        """
                        INSERT INTO source_posts (
                            run_id, post_id, post_url, author_handle, posted_at,
                            title, summary, selection_reason, content_excerpt, collected_at, raw_rank
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        values,
                    )
                    source_post_id = int(cursor.lastrowid)
                else:
                    connection.execute(
                        """
                        UPDATE source_posts
                        SET run_id = ?, post_id = ?, post_url = ?, author_handle = ?, posted_at = ?,
                            title = ?, summary = ?, selection_reason = ?, content_excerpt = ?,
                            collected_at = ?, raw_rank = ?
                        WHERE id = ?
                        """,
                        values + (source_post_id,),
                    )
                source_post_ids[post.source_key] = source_post_id
        return source_post_ids

    def save_digest(self, draft: DigestDraft, channel_id: int) -> int:
        existing = self.get_digest_by_date(draft.digest_date)
        now = utcnow_iso()
        with self._connect() as connection:
            if existing:
                connection.execute(
                    """
                    UPDATE digest_messages
                    SET headline = ?, overview = ?, summary_markdown = ?, discord_channel_id = ?,
                        status = ?, created_at = ?, posted_at = NULL, failure_reason = NULL, discord_message_ids = NULL
                    WHERE id = ?
                    """,
                    (
                        draft.headline,
                        draft.overview,
                        draft.markdown,
                        str(channel_id),
                        DigestStatus.PENDING.value,
                        now,
                        existing["id"],
                    ),
                )
                return int(existing["id"])

            cursor = connection.execute(
                """
                INSERT INTO digest_messages (
                    digest_date, headline, overview, summary_markdown, discord_channel_id,
                    status, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    draft.digest_date.isoformat(),
                    draft.headline,
                    draft.overview,
                    draft.markdown,
                    str(channel_id),
                    DigestStatus.PENDING.value,
                    now,
                ),
            )
            return int(cursor.lastrowid)

    def attach_digest_items(self, digest_id: int, source_post_ids: dict[str, int], items: list[Any]) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM digest_items WHERE digest_message_id = ?", (digest_id,))
            for item in items:
                source_id = source_post_ids.get(item.source.source_key)
                if source_id is None:
                    continue
                connection.execute(
                    """
                    INSERT INTO digest_items (digest_message_id, source_post_id, rank_order, selection_reason)
                    VALUES (?, ?, ?, ?)
                    """,
                    (digest_id, source_id, item.rank_order, item.selection_reason),
                )

    def mark_digest_posted(self, digest_id: int, message_ids: list[int]) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE digest_messages
                SET status = ?, posted_at = ?, discord_message_ids = ?, failure_reason = NULL
                WHERE id = ?
                """,
                (DigestStatus.POSTED.value, utcnow_iso(), json.dumps(message_ids), digest_id),
            )

    def mark_digest_failed(self, digest_id: int, error_message: str) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE digest_messages
                SET status = ?, failure_reason = ?
                WHERE id = ?
                """,
                (DigestStatus.FAILED.value, error_message, digest_id),
            )

    def _find_source_post_id(self, connection: sqlite3.Connection, post_id: str | None, post_url: str | None) -> int | None:
        if post_id:
            row = connection.execute(
                "SELECT id FROM source_posts WHERE post_id = ?",
                (post_id,),
            ).fetchone()
            if row:
                return int(row["id"])

        if post_url:
            row = connection.execute(
                "SELECT id FROM source_posts WHERE post_url = ?",
                (post_url,),
            ).fetchone()
            if row:
                return int(row["id"])
        return None

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._db_path)
        connection.row_factory = sqlite3.Row
        return connection
