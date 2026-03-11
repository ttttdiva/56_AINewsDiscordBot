from __future__ import annotations

from functools import lru_cache
from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"


@lru_cache(maxsize=None)
def load_prompt_template(name: str) -> str:
    path = PROMPTS_DIR / name
    return path.read_text(encoding="utf-8").strip()


def render_prompt_template(name: str, **kwargs: object) -> str:
    template = load_prompt_template(name)
    return template.format(**kwargs)
