"""Heuristic detection of token-like strings in generated patch text."""

from __future__ import annotations

import re

# Named groups for logging only — patterns are conservative (length-bound).
_SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("github_pat", re.compile(r"ghp_[0-9a-zA-Z]{20,}")),
    ("github_oauth", re.compile(r"gho_[0-9a-zA-Z]{20,}")),
    ("gemini_api_key", re.compile(r"AIza[0-9A-Za-z\-_]{20,}")),
    ("openai_sk", re.compile(r"sk-[a-zA-Z0-9]{20,}")),
    ("anthropic_sk", re.compile(r"sk-ant-[a-zA-Z0-9\-_]{10,}")),
)


def patch_secret_hits(blob: str) -> list[str]:
    """Return pattern names that matched (empty if none)."""
    if not blob:
        return []
    hits: list[str] = []
    for name, rx in _SECRET_PATTERNS:
        if rx.search(blob):
            hits.append(name)
    return hits
