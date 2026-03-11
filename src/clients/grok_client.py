from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from src.config.settings import AppSettings

logger = logging.getLogger(__name__)


class GrokAPIError(RuntimeError):
    """Raised when the Grok API request fails."""


def extract_text_from_response(payload: dict[str, Any]) -> str:
    output_text = payload.get("output_text")
    if output_text:
        if isinstance(output_text, list):
            return "\n".join(str(part) for part in output_text).strip()
        return str(output_text).strip()

    outputs = payload.get("output")
    if not isinstance(outputs, list):
        return json.dumps(payload, ensure_ascii=False)

    texts: list[str] = []
    for item in outputs:
        if not isinstance(item, dict):
            continue
        if item.get("type") != "message":
            continue
        content = item.get("content", [])
        if isinstance(content, str):
            if content:
                texts.append(content)
            continue
        if not isinstance(content, list):
            continue
        for block in content:
            if isinstance(block, str):
                if block:
                    texts.append(block)
                continue
            if not isinstance(block, dict):
                continue
            if block.get("type") in {"output_text", "text"}:
                text_value = block.get("text") or block.get("output_text")
                if text_value:
                    texts.append(str(text_value))

    return "\n".join(texts).strip() if texts else json.dumps(payload, ensure_ascii=False)


def extract_json_object(text: str) -> dict[str, Any]:
    candidate = text.strip()
    if candidate.startswith("```"):
        lines = candidate.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        candidate = "\n".join(lines).strip()

    try:
        value = json.loads(candidate)
        if isinstance(value, dict):
            return value
        raise ValueError("Top-level JSON must be an object")
    except json.JSONDecodeError:
        pass

    for opener, closer in (("{", "}"), ("[", "]")):
        start = candidate.find(opener)
        if start < 0:
            continue
        depth = 0
        in_string = False
        escaped = False
        for index in range(start, len(candidate)):
            char = candidate[index]
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue

            if char == '"':
                in_string = True
                continue
            if char == opener:
                depth += 1
            elif char == closer:
                depth -= 1
                if depth == 0:
                    raw = candidate[start : index + 1]
                    value = json.loads(raw)
                    if isinstance(value, dict):
                        return value
                    raise ValueError("Top-level JSON must be an object")

    raise ValueError("Could not extract a JSON object from the Grok response")


class GrokClient:
    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings

    async def create_response(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        tools: list[dict[str, Any]] | None = None,
        max_output_tokens: int = 1500,
    ) -> tuple[dict[str, Any], str]:
        if not self._settings.xai_api_key:
            raise GrokAPIError("XAI_API_KEY is not configured.")

        payload = {
            "model": self._settings.xai_grok_model,
            "input": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.1,
            "max_output_tokens": max_output_tokens,
        }
        if tools:
            payload["tools"] = tools

        headers = {
            "Authorization": f"Bearer {self._settings.xai_api_key}",
            "Content-Type": "application/json",
            "User-Agent": "AINewsDiscordBot/0.1",
        }
        url = f"{self._settings.xai_api_base.rstrip('/')}/responses"

        async with httpx.AsyncClient(timeout=self._settings.grok_timeout_seconds, headers=headers) as client:
            try:
                response = await client.post(url, json=payload)
            except httpx.TimeoutException as exc:
                raise GrokAPIError("Grok API request timed out") from exc

        if response.status_code >= 400:
            try:
                error_payload = response.json()
            except ValueError:
                error_payload = response.text
            raise GrokAPIError(f"Grok API error ({response.status_code}): {error_payload}")

        response_payload = response.json()
        text = extract_text_from_response(response_payload)
        if not text:
            raise GrokAPIError("Grok API returned an empty response")

        logger.debug("Grok response text: %s", text)
        return response_payload, text

    async def search_ai_news(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        from_date: str,
        to_date: str,
    ) -> tuple[dict[str, Any], str]:
        tool: dict[str, Any] = {"type": "x_search", "from_date": from_date, "to_date": to_date}
        if self._settings.allowed_x_handles:
            tool["allowed_x_handles"] = self._settings.allowed_x_handles
        if self._settings.excluded_x_handles:
            tool["excluded_x_handles"] = self._settings.excluded_x_handles
        return await self.create_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            tools=[tool],
            max_output_tokens=1500,
        )
