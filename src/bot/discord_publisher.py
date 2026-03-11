from __future__ import annotations

import asyncio
import logging

import discord

logger = logging.getLogger(__name__)


def split_message(content: str, limit: int = 2000) -> list[str]:
    if len(content) <= limit:
        return [content]

    chunks: list[str] = []
    remaining = content
    while remaining:
        if len(remaining) <= limit:
            chunks.append(remaining)
            break

        split_at = remaining.rfind("\n\n", 0, limit)
        if split_at < 0:
            split_at = remaining.rfind("\n", 0, limit)
        if split_at < 0:
            split_at = limit

        chunk = remaining[:split_at].strip()
        if not chunk:
            chunk = remaining[:limit]
            split_at = limit
        chunks.append(chunk)
        remaining = remaining[split_at:].lstrip()
    return chunks


class _OneShotDiscordClient(discord.Client):
    def __init__(self, channel_id: int, messages: list[str]) -> None:
        intents = discord.Intents.none()
        intents.guilds = True
        super().__init__(intents=intents)
        self._channel_id = channel_id
        self._messages = messages
        self.result: asyncio.Future[list[int]] = asyncio.get_running_loop().create_future()

    async def on_ready(self) -> None:
        try:
            channel = self.get_channel(self._channel_id)
            if channel is None:
                channel = await self.fetch_channel(self._channel_id)

            message_ids: list[int] = []
            for message in self._messages:
                sent = await channel.send(message)  # type: ignore[attr-defined]
                message_ids.append(sent.id)

            self.result.set_result(message_ids)
        except Exception as exc:  # pragma: no cover
            logger.exception("Failed to publish to Discord")
            self.result.set_exception(exc)
        finally:
            await self.close()


class DiscordPublisher:
    def __init__(self, token: str) -> None:
        self._token = token

    async def publish(self, markdown: str, channel_id: int) -> list[int]:
        if not self._token:
            raise RuntimeError("DISCORD_BOT_TOKEN is not configured.")

        messages = split_message(markdown)
        client = _OneShotDiscordClient(channel_id, messages)
        start_task = asyncio.create_task(client.start(self._token))
        try:
            return await client.result
        finally:
            await start_task
