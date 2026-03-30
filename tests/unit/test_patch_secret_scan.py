"""Tests for heuristic patch secret scanning."""

from contribai.orchestrator.patch_secret_scan import patch_secret_hits


def test_patch_secret_hits_empty():
    assert patch_secret_hits("") == []
    assert patch_secret_hits("no tokens here") == []


def test_patch_secret_hits_github_pat():
    blob = "token = ghp_abcdefghijklmnopqrst"
    assert patch_secret_hits(blob) == ["github_pat"]


def test_patch_secret_hits_gemini():
    blob = "key=AIzaSyDummyKey0123456789abcdefghij"
    assert "gemini_api_key" in patch_secret_hits(blob)


def test_patch_secret_hits_openai_sk():
    blob = "export OPENAI_API_KEY=sk-12345678901234567890abcdef"
    assert "openai_sk" in patch_secret_hits(blob)


def test_patch_secret_hits_multiple():
    blob = "x=ghp_abcdefghijklmnopqrst && y=sk-12345678901234567890abcd"
    hits = patch_secret_hits(blob)
    assert "github_pat" in hits
    assert "openai_sk" in hits
