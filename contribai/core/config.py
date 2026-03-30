"""Pydantic-based configuration system for ContribAI."""

from __future__ import annotations

import os
import subprocess
from fnmatch import fnmatch
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, model_validator

from contribai.core.exceptions import ConfigError


class GitHubConfig(BaseModel):
    """GitHub API configuration."""

    token: str = ""
    max_repos_per_run: int = 5
    max_prs_per_day: int = 10
    # Cap findings → PRs per repo in one pipeline pass (after validation).
    max_prs_per_repo_per_run: int = 3
    rate_limit_buffer: int = 100
    dco_signoff: bool = True  # Auto-append Signed-off-by to commit messages
    # Scan generated patch for strings resembling API keys before opening PR.
    # off = skip; warn = log only; block = do not create PR if matched.
    secret_scan_mode: Literal["off", "warn", "block"] = "warn"

    @model_validator(mode="after")
    def resolve_token(self):
        """Fallback: $GITHUB_TOKEN env var → `gh auth token` CLI."""
        if not self.token:
            self.token = os.environ.get("GITHUB_TOKEN", "")
        if not self.token:
            try:
                result = subprocess.run(
                    ["gh", "auth", "token"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0 and result.stdout.strip():
                    self.token = result.stdout.strip()
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass
        return self


class LLMKeyPoolConfig(BaseModel):
    """Multi-key rotation for Gemini API key auth (e.g. many free-tier keys in YAML)."""

    enabled: bool = False
    cooldown_transient_sec: float = 45.0
    cooldown_rate_soft_sec: float = 120.0
    cooldown_quota_long_sec: float = 86_400.0
    max_rotations_per_request: int = 12
    client_cache_size: int = 32
    max_concurrent_per_key: int = 2
    state_path: str = "~/.contribai/gemini_key_pool_state.json"


class LLMConfig(BaseModel):
    """LLM provider configuration."""

    provider: Literal["gemini", "openai", "anthropic", "ollama"] = "gemini"
    model: str = "gemini-2.5-flash"
    api_key: str = ""
    api_keys: list[str] = Field(default_factory=list)
    key_pool: LLMKeyPoolConfig = Field(default_factory=LLMKeyPoolConfig)
    # Minimum seconds between consecutive LLM HTTP calls (per process). Helps avoid RPM bursts.
    min_request_interval_sec: float = 0.0
    temperature: float = 0.3
    max_tokens: int = 8192
    base_url: str | None = None  # for ollama or custom endpoints
    # Vertex AI (Google Cloud)
    vertex_project: str = ""
    vertex_location: str = "global"

    def merged_gemini_api_keys(self) -> list[str]:
        """Ordered de-duplicated keys: `api_key` first, then `api_keys`."""
        out: list[str] = []
        for raw in (self.api_key, *self.api_keys):
            s = (raw or "").strip()
            if s and s not in out:
                out.append(s)
        return out

    @model_validator(mode="after")
    def resolve_api_key_and_defaults(self):
        """Fallback: env vars for API keys + default model per provider."""
        if not self.api_key:
            env_map = {
                "gemini": "GEMINI_API_KEY",
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
            }
            env_var = env_map.get(self.provider, "")
            if env_var:
                self.api_key = os.environ.get(env_var, "")
        # Vertex AI: project from env
        if not self.vertex_project:
            self.vertex_project = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
        # Default model per provider
        if self.model == "gemini-2.5-flash" and self.provider != "gemini":
            default_models = {
                "openai": "gpt-4o",
                "anthropic": "claude-sonnet-4-20250514",
                "ollama": "codellama:13b",
            }
            self.model = default_models.get(self.provider, self.model)
        return self

    @property
    def use_vertex(self) -> bool:
        """Whether to use Vertex AI instead of API key auth."""
        return bool(self.vertex_project)

    def has_llm_credentials(self) -> bool:
        """True if the configured provider can run (keys or Vertex / local)."""
        if self.use_vertex:
            return bool(self.vertex_project)
        if self.provider == "gemini":
            return bool(self.merged_gemini_api_keys())
        if self.provider == "ollama":
            return True
        return bool(self.api_key.strip())


class AnalysisConfig(BaseModel):
    """Analysis engine configuration."""

    enabled_analyzers: list[str] = Field(
        default_factory=lambda: ["security", "code_quality", "docs", "ui_ux"]
    )
    severity_threshold: Literal["low", "medium", "high", "critical"] = "medium"
    max_file_size_kb: int = 500
    skip_patterns: list[str] = Field(
        default_factory=lambda: ["*.min.js", "*.min.css", "vendor/*", "node_modules/*", "*.lock"]
    )
    max_context_tokens: int = 30_000  # token budget for context compression
    # Cap parallel analyzer strategies (each may call LLM). Lower = gentler on RPM (e.g. free tier).
    max_concurrent_analyzers: int = 2
    # Gemini: ask for application/json in analyzer output. Disable if the model/API errors.
    use_gemini_json_mode: bool = True


class ContributionConfig(BaseModel):
    """Contribution generation configuration."""

    enabled_types: list[str] = Field(
        default_factory=lambda: [
            "security_fix",
            "docs_improve",
            "code_quality",
            "feature_add",
            "ui_ux_fix",
            "performance_opt",
            "refactor",
        ]
    )
    max_files_per_pr: int = 10
    run_tests_before_pr: bool = True
    commit_convention: Literal["conventional", "angular", "none"] = "conventional"
    pr_description_style: Literal["minimal", "detailed"] = "detailed"


class DiscoveryConfig(BaseModel):
    """Repository discovery configuration."""

    languages: list[str] = Field(default_factory=lambda: ["python"])
    stars_range: list[int] = Field(default_factory=lambda: [50, 10000])
    min_last_activity_days: int = 30
    require_contributing_guide: bool = False
    topics: list[str] = Field(default_factory=list)
    # If non-empty, only repos matching these patterns (fnmatch or exact owner/repo) are used.
    repo_allowlist: list[str] = Field(default_factory=list)
    # False = ignore repo_allowlist everywhere (discovery, hunt, target). Default True = enforce.
    enforce_repo_allowlist: bool = True

    def allows_repo(self, full_name: str) -> bool:
        """True if allowlist enforcement is off, list empty, or full_name matches an entry."""
        if not self.enforce_repo_allowlist:
            return True
        if not self.repo_allowlist:
            return True
        fn_lc = full_name.strip().lower()
        for raw in self.repo_allowlist:
            pat = (raw or "").strip().lower()
            if not pat:
                continue
            if fn_lc == pat or fnmatch(fn_lc, pat):
                return True
        return False


class StorageConfig(BaseModel):
    """Storage / memory configuration."""

    db_path: str = "~/.contribai/memory.db"
    cache_ttl_hours: int = 24

    @property
    def resolved_db_path(self) -> Path:
        return Path(self.db_path).expanduser()


class SchedulerConfig(BaseModel):
    """Scheduler configuration for cron-based runs."""

    enabled: bool = False
    cron: str = "0 */6 * * *"  # every 6 hours
    timezone: str = "UTC"
    max_concurrent: int = 3


class WebConfig(BaseModel):
    """Web dashboard configuration."""

    host: str = "127.0.0.1"
    port: int = 8787
    enabled: bool = True
    api_keys: list[str] = Field(default_factory=list)
    webhook_secret: str = ""


class PipelineConfig(BaseModel):
    """Pipeline execution configuration."""

    max_concurrent_repos: int = 3
    timeout_per_repo_sec: int = 300
    inter_repo_delay_sec: float = 5.0  # delay between repos to avoid rate limits
    max_retries: int = 2  # middleware retry count
    min_quality_score: float = 5.0  # quality gate threshold
    human_review: bool = False  # pause for human approval before creating PRs
    # Skip opening new PRs if we created one for this repo within the last N hours (0 = disabled).
    repo_pr_cooldown_hours: float = 0.0
    # If True and discovery.repo_allowlist is empty, log a warning on non-dry pipeline runs.
    warn_when_live_without_repo_allowlist: bool = True


class QuotaConfig(BaseModel):
    """API usage quota configuration."""

    github_daily_limit: int = 5000
    llm_daily_limit: int = 1000
    llm_daily_tokens: int = 1_000_000


class NotificationConfig(BaseModel):
    """Notification channel configuration."""

    slack_webhook: str = ""
    discord_webhook: str = ""
    telegram_token: str = ""
    telegram_chat_id: str = ""
    on_merge: bool = True
    on_close: bool = True
    on_run_complete: bool = True


class MultiModelConfig(BaseModel):
    """Multi-model routing configuration."""

    enabled: bool = False
    strategy: str = "balanced"  # performance | balanced | economy
    # Per-task model overrides (task_type → model_name)
    model_overrides: dict[str, str] = Field(default_factory=dict)


class SandboxConfig(BaseModel):
    """Sandbox execution configuration."""

    enabled: bool = False
    timeout: int = 30
    docker_image: str = ""  # override default language image


class ContribAIConfig(BaseModel):
    """Root configuration for ContribAIConfig."""

    github: GitHubConfig = Field(default_factory=GitHubConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig)
    contribution: ContributionConfig = Field(default_factory=ContributionConfig)
    discovery: DiscoveryConfig = Field(default_factory=DiscoveryConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    scheduler: SchedulerConfig = Field(default_factory=SchedulerConfig)
    web: WebConfig = Field(default_factory=WebConfig)
    pipeline: PipelineConfig = Field(default_factory=PipelineConfig)
    quota: QuotaConfig = Field(default_factory=QuotaConfig)
    notifications: NotificationConfig = Field(default_factory=NotificationConfig)
    multi_model: MultiModelConfig = Field(default_factory=MultiModelConfig)
    sandbox: SandboxConfig = Field(default_factory=SandboxConfig)


def load_config(path: str | Path | None = None) -> ContribAIConfig:
    """Load configuration from YAML file.

    Priority: explicit path > ./config.yaml > ~/.contribai/config.yaml > defaults
    """
    search_paths = [
        Path(path) if path else None,
        Path("config.yaml"),
        Path.home() / ".contribai" / "config.yaml",
    ]

    for p in search_paths:
        if p and p.exists():
            try:
                raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
                return ContribAIConfig(**raw)
            except yaml.YAMLError as e:
                raise ConfigError(f"Invalid YAML in {p}: {e}") from e
            except Exception as e:
                raise ConfigError(f"Failed to load config from {p}: {e}") from e

    # No config file found - use defaults
    return ContribAIConfig()
