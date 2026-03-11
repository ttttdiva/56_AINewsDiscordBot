from __future__ import annotations

import asyncio
import json
import logging
import threading
from datetime import datetime
from pathlib import Path

from src.bot.discord_publisher import DiscordPublisher
from src.clients.grok_client import GrokClient
from src.config.settings import AppSettings, RunMode
from src.models.news import CollectionResult, DigestDraft, RunStatus
from src.services.collector import NewsCollector
from src.services.filtering import NewsFilter
from src.services.summarizer import DigestBuilder
from src.storage.sqlite_repository import SQLiteStateRepository

logger = logging.getLogger(__name__)


class AppRunner:
    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings
        self._settings.ensure_runtime_dirs()
        self._repository = SQLiteStateRepository(settings.state_db_abspath)
        self._repository.initialize()
        self._collector = NewsCollector(settings, GrokClient(settings))
        self._filter = NewsFilter(settings.digest_max_items)
        self._builder = DigestBuilder()
        self._run_lock = threading.Lock()

    def run_sync(self, mode: RunMode) -> int:
        if not self._run_lock.acquire(blocking=False):
            logger.warning("Another run is already in progress. Skipping %s.", mode.value)
            return 1

        try:
            return asyncio.run(self._run_once(mode))
        finally:
            self._run_lock.release()

    async def _run_once(self, mode: RunMode) -> int:
        digest_date = datetime.now(self._settings.timezone).date()
        run_id = self._repository.start_run(mode.value)
        digest_id: int | None = None

        try:
            existing_digest = self._repository.get_digest_by_date(digest_date)
            if mode is not RunMode.DRY_RUN and existing_digest and existing_digest["status"] == "posted":
                logger.info("Digest already posted for %s. Skipping.", digest_date.isoformat())
                self._repository.finish_run(run_id, RunStatus.SKIPPED)
                return 0

            collection = await self._collector.collect(digest_date)
            selected_posts = self._filter.filter_posts(
                collection.items,
                self._repository.get_posted_source_keys(),
            )
            draft = self._builder.build(digest_date, collection.headline, collection.overview, selected_posts)

            artifact_paths = self._write_artifacts(collection, draft, mode)
            logger.info("Artifacts written to %s", ", ".join(str(path) for path in artifact_paths))

            if mode is RunMode.DRY_RUN:
                print(draft.markdown)
                self._repository.finish_run(run_id, RunStatus.SUCCESS)
                return 0

            source_post_ids = self._repository.upsert_source_posts(run_id, selected_posts)
            digest_id = self._repository.save_digest(draft, self._settings.discord_channel_id)
            self._repository.attach_digest_items(digest_id, source_post_ids, draft.items)

            publisher = DiscordPublisher(self._settings.discord_bot_token or "")
            message_ids = await publisher.publish(draft.markdown, self._settings.discord_channel_id)
            self._repository.mark_digest_posted(digest_id, message_ids)
            self._repository.finish_run(run_id, RunStatus.SUCCESS)
            logger.info("Digest posted successfully. message_ids=%s", message_ids)
            return 0
        except Exception as exc:
            logger.exception("Run failed")
            if digest_id is not None:
                self._repository.mark_digest_failed(digest_id, str(exc))
            self._repository.finish_run(run_id, RunStatus.FAILED, str(exc))
            return 1

    def _write_artifacts(self, collection: CollectionResult, draft: DigestDraft, mode: RunMode) -> list[Path]:
        timestamp = datetime.now(self._settings.timezone).strftime("%Y%m%d-%H%M%S")
        stem = f"{timestamp}-{mode.value}"
        raw_dir = self._settings.raw_output_dir_abspath
        response_path = raw_dir / f"{stem}-response.json"
        normalized_path = raw_dir / f"{stem}-normalized.json"
        markdown_path = raw_dir / f"{stem}-digest.md"

        response_path.write_text(
            json.dumps(collection.raw_response_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        normalized_path.write_text(
            json.dumps(collection.model_dump(mode="json"), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        markdown_path.write_text(draft.markdown, encoding="utf-8")
        return [response_path, normalized_path, markdown_path]
