"""Gemini API key pool: rotation, cooldowns, and error classification.

Designed for many low-quota (e.g. free-tier) keys configured via YAML `llm.api_keys`.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import re
import time
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

from contribai.core.config import LLMKeyPoolConfig

logger = logging.getLogger(__name__)


class GeminiErrorKind(StrEnum):
    TRANSIENT = "transient"
    RATE_SOFT = "rate_soft"
    QUOTA_LONG = "quota_long"
    INVALID_KEY = "invalid_key"
    PERMISSION = "permission"
    UNKNOWN = "unknown"


@dataclass
class ClassifiedGeminiError:
    kind: GeminiErrorKind
    retry_after_sec: float | None
    message: str


def _key_fingerprint(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()[:16]


_RETRY_AFTER_RE = re.compile(
    r"retry\s*(?:after|in)?\s*[:\"]?\s*(\d+(?:\.\d+)?)\s*s",
    re.IGNORECASE,
)


def classify_gemini_error(exc: BaseException) -> ClassifiedGeminiError:
    """Map Google GenAI / HTTP failures to pool policy.

    Uses structured fields when present, else string heuristics.
    """
    raw = str(exc)
    lower = raw.lower()
    m = _RETRY_AFTER_RE.search(raw)
    retry_after = float(m.group(1)) if m else None

    if any(x in lower for x in ("api key not valid", "invalid api key", "api_key_invalid")):
        return ClassifiedGeminiError(GeminiErrorKind.INVALID_KEY, retry_after, raw[:500])

    status: int | None = None
    for attr in ("status_code", "code"):
        v = getattr(exc, attr, None)
        if isinstance(v, int):
            status = v
            break
    details = getattr(exc, "details", None) or getattr(exc, "response", None)
    if status is None and details is not None:
        status = getattr(details, "status_code", None)

    if (status == 403 or "permission" in lower or "forbidden" in lower) and (
        "rate" not in lower and "quota" not in lower
    ):
        return ClassifiedGeminiError(GeminiErrorKind.PERMISSION, retry_after, raw[:500])

    if status == 429 or "resource_exhausted" in lower or "resource exhausted" in lower:
        if any(x in lower for x in ("per day", "daily", "rpd", "generate_requests_per_day")):
            return ClassifiedGeminiError(GeminiErrorKind.QUOTA_LONG, retry_after, raw[:500])
        return ClassifiedGeminiError(GeminiErrorKind.RATE_SOFT, retry_after, raw[:500])

    if any(
        x in lower
        for x in (
            "quota exceeded",
            "exceeded your",
            "billing",
            "limit: generatecontent",
        )
    ):
        return ClassifiedGeminiError(GeminiErrorKind.QUOTA_LONG, retry_after, raw[:500])

    if any(x in lower for x in ("rate", "throttl", "too many requests")):
        return ClassifiedGeminiError(GeminiErrorKind.RATE_SOFT, retry_after, raw[:500])

    if status is not None and status >= 500:
        return ClassifiedGeminiError(GeminiErrorKind.TRANSIENT, retry_after, raw[:500])
    if any(x in lower for x in ("timeout", "temporarily", "unavailable", "connection")):
        return ClassifiedGeminiError(GeminiErrorKind.TRANSIENT, retry_after, raw[:500])

    return ClassifiedGeminiError(GeminiErrorKind.UNKNOWN, retry_after, raw[:500])


@dataclass
class KeyRecord:
    api_key: str
    key_id: str = field(init=False)
    cooldown_until: float = 0.0
    disabled: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "key_id", _key_fingerprint(self.api_key))


class KeyPool:
    """Thread-safe async key pool with cooldowns and optional JSON persistence."""

    def __init__(self, keys: list[str], cfg: LLMKeyPoolConfig) -> None:
        if not keys:
            raise ValueError("KeyPool requires at least one API key")
        self._cfg = cfg
        self._records = [KeyRecord(k) for k in keys]
        self._lock = asyncio.Lock()
        self._rr = 0
        lim = cfg.max_concurrent_per_key
        sem_limit = lim if lim and lim > 0 else 10_000
        self._semaphores = {r.key_id: asyncio.Semaphore(sem_limit) for r in self._records}
        sp = (cfg.state_path or "").strip()
        self._state_path = Path(sp).expanduser() if sp else None
        self._load_state()

    def _load_state(self) -> None:
        if not self._state_path or not self._state_path.is_file():
            return
        try:
            data = json.loads(self._state_path.read_text(encoding="utf-8"))
            by_id: dict[str, Any] = data.get("keys", {})
            for r in self._records:
                row = by_id.get(r.key_id)
                if not row:
                    continue
                if row.get("disabled"):
                    r.disabled = True
                cu = row.get("cooldown_until")
                if isinstance(cu, (int, float)):
                    r.cooldown_until = float(cu)
        except Exception:
            logger.debug("Failed to load key pool state from %s", self._state_path, exc_info=True)

    def _save_state_unlocked(self) -> None:
        if not self._state_path:
            return
        payload = {
            "keys": {
                r.key_id: {
                    "disabled": r.disabled,
                    "cooldown_until": r.cooldown_until,
                }
                for r in self._records
            }
        }
        try:
            self._state_path.parent.mkdir(parents=True, exist_ok=True)
            self._state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except Exception:
            logger.debug("Failed to save key pool state", exc_info=True)

    def _eligible(self, r: KeyRecord) -> bool:
        if r.disabled:
            return False
        return time.time() >= r.cooldown_until

    def _pick_unlocked(self) -> KeyRecord | None:
        n = len(self._records)
        for i in range(n):
            idx = (self._rr + i) % n
            r = self._records[idx]
            if self._eligible(r):
                self._rr = (idx + 1) % n
                return r
        return None

    async def pick(self) -> KeyRecord | None:
        async with self._lock:
            return self._pick_unlocked()

    def cooldown_seconds(self, classified: ClassifiedGeminiError) -> float:
        cfg = self._cfg
        if classified.retry_after_sec is not None and classified.retry_after_sec > 0:
            return min(classified.retry_after_sec, cfg.cooldown_quota_long_sec)
        match classified.kind:
            case GeminiErrorKind.TRANSIENT:
                return cfg.cooldown_transient_sec
            case GeminiErrorKind.RATE_SOFT:
                return cfg.cooldown_rate_soft_sec
            case GeminiErrorKind.QUOTA_LONG:
                return cfg.cooldown_quota_long_sec
            case GeminiErrorKind.INVALID_KEY | GeminiErrorKind.PERMISSION:
                return cfg.cooldown_quota_long_sec
            case _:
                return cfg.cooldown_rate_soft_sec

    async def apply_failure(self, rec: KeyRecord, classified: ClassifiedGeminiError) -> None:
        async with self._lock:
            if classified.kind in (GeminiErrorKind.INVALID_KEY, GeminiErrorKind.PERMISSION):
                rec.disabled = True
                logger.warning(
                    "Gemini key %s disabled (%s)",
                    rec.key_id,
                    classified.kind,
                )
            else:
                sec = self.cooldown_seconds(classified)
                rec.cooldown_until = time.time() + sec
                logger.warning(
                    "Gemini key %s cooldown %.0fs (%s)",
                    rec.key_id,
                    sec,
                    classified.kind,
                )
            self._save_state_unlocked()

    async def mark_success(self, rec: KeyRecord) -> None:
        async with self._lock:
            rec.cooldown_until = 0.0

    def semaphore_for(self, rec: KeyRecord) -> asyncio.Semaphore:
        return self._semaphores[rec.key_id]

    def exhausted_message(self) -> tuple[str, float | None]:
        soonest: float | None = None
        parts: list[str] = []
        now = time.time()
        for r in self._records:
            if r.disabled:
                parts.append(f"{r.key_id}:disabled")
                continue
            if r.cooldown_until > now:
                parts.append(f"{r.key_id}:cooldown~{int(r.cooldown_until - now)}s")
                soonest = r.cooldown_until if soonest is None else min(soonest, r.cooldown_until)
        return "; ".join(parts) or "no keys", soonest

    @property
    def max_rotations_per_request(self) -> int:
        return self._cfg.max_rotations_per_request


class GeminiClientCache:
    """Small LRU cache of genai.Client instances keyed by key_id."""

    def __init__(self, max_size: int) -> None:
        self._max = max(1, max_size)
        self._clients: OrderedDict[str, Any] = OrderedDict()

    def get(self, key_id: str, factory: Callable[[], Any]) -> Any:
        if key_id in self._clients:
            self._clients.move_to_end(key_id)
            return self._clients[key_id]
        client = factory()
        self._clients[key_id] = client
        self._clients.move_to_end(key_id)
        while len(self._clients) > self._max:
            self._clients.popitem(last=False)
        return client
