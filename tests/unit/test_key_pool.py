"""Tests for Gemini API key pool and error classification."""

import pytest

from contribai.core.config import LLMConfig, LLMKeyPoolConfig
from contribai.llm.key_pool import (
    GeminiErrorKind,
    KeyPool,
    classify_gemini_error,
)


class TestClassifyGeminiError:
    def test_429_daily_quota(self):
        c = classify_gemini_error(Exception("429 Resource exhausted: per day limit"))
        assert c.kind == GeminiErrorKind.QUOTA_LONG

    def test_429_rpm(self):
        c = classify_gemini_error(Exception("429 too many requests"))
        assert c.kind == GeminiErrorKind.RATE_SOFT

    def test_invalid_api_key_message(self):
        c = classify_gemini_error(Exception("API key not valid. Please pass a valid API key."))
        assert c.kind == GeminiErrorKind.INVALID_KEY

    def test_transient_503(self):
        c = classify_gemini_error(Exception("503 Service Unavailable"))
        assert c.kind == GeminiErrorKind.TRANSIENT

    def test_retry_after_parsed(self):
        c = classify_gemini_error(Exception("retry after 33.5s"))
        assert c.retry_after_sec == 33.5


class TestKeyPool:
    @pytest.mark.asyncio
    async def test_round_robin_two_keys(self):
        cfg = LLMKeyPoolConfig(enabled=True, max_rotations_per_request=5, state_path="")
        pool = KeyPool(["key-a", "key-b"], cfg)
        a = await pool.pick()
        b = await pool.pick()
        assert {a.api_key, b.api_key} == {"key-a", "key-b"}

    @pytest.mark.asyncio
    async def test_cooldown_skips_key(self):
        cfg = LLMKeyPoolConfig(
            enabled=True,
            max_rotations_per_request=5,
            state_path="",
            cooldown_rate_soft_sec=3600.0,
        )
        pool = KeyPool(["only-one"], cfg)
        rec = await pool.pick()
        assert rec is not None
        from contribai.llm.key_pool import ClassifiedGeminiError

        await pool.apply_failure(
            rec,
            ClassifiedGeminiError(GeminiErrorKind.RATE_SOFT, None, "slow down"),
        )
        assert await pool.pick() is None
        msg, _ = pool.exhausted_message()
        assert "cooldown" in msg or "disabled" in msg

    @pytest.mark.asyncio
    async def test_invalid_disables_key(self):
        cfg = LLMKeyPoolConfig(enabled=True, state_path="")
        pool = KeyPool(["bad"], cfg)
        rec = await pool.pick()
        assert rec is not None
        from contribai.llm.key_pool import ClassifiedGeminiError

        await pool.apply_failure(
            rec,
            ClassifiedGeminiError(GeminiErrorKind.INVALID_KEY, None, "invalid"),
        )
        assert (await pool.pick()) is None


class TestMergedGeminiKeys:
    def test_order_and_dedupe(self):
        c = LLMConfig(
            api_key=" first ",
            api_keys=["second", " first ", "third", "second"],
        )
        assert c.merged_gemini_api_keys() == ["first", "second", "third"]


class TestLLMConfigHasCredentials:
    def test_gemini_from_list_only(self):
        c = LLMConfig(provider="gemini", api_key="", api_keys=["k1"])
        assert c.has_llm_credentials()

    def test_gemini_empty(self):
        c = LLMConfig(provider="gemini", api_key="", api_keys=[])
        assert not c.has_llm_credentials()
