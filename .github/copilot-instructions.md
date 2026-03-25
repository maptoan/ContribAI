# Copilot Instructions for ContribAI

## Project Context
ContribAI is an autonomous AI agent that contributes to GitHub open source projects.
It discovers repos, analyzes code, generates fixes, and submits PRs automatically.

## Architecture (v2.4.0)
- **Pipeline**: Discovery → Middleware → Analysis → Generation → PR → CI Monitor
- **Middleware chain**: `contribai/core/middleware.py` (RateLimit, Validation, Retry, DCO, QualityGate)
- **Skills**: `contribai/analysis/skills.py` (17 skills, progressive loading by language/framework)
- **Sub-agents**: `contribai/agents/registry.py` (Analyzer, Generator, Patrol, Compliance)
- **Tools**: `contribai/tools/protocol.py` (MCP-inspired protocol with GitHubTool, LLMTool)
- **Memory**: `contribai/orchestrator/memory.py` (SQLite, 6 tables including outcome learning)

## Code Style
- Python 3.11+, fully async (asyncio)
- `from __future__ import annotations` in every file
- Google-style docstrings
- ruff for linting and formatting (100 char line limit)
- Full type hints with `str | None` syntax
- `snake_case` functions, `PascalCase` classes

## Key Patterns
- All LLM calls: `await self._llm.complete(prompt, system_prompt=...)`
- All GitHub API: `await self._github.method(owner, repo, ...)`
- Config: `ContribAIConfig.from_yaml("config.yaml")`
- Memory: `await memory.method(...)` (aiosqlite)
- Errors: `try/except` with `logger.error()`, never bare except

## Important Rules
- NEVER modify: LICENSE, CONTRIBUTING.md, CODE_OF_CONDUCT.md
- ONLY modify code files (.py, .js, .ts, .go, .rs, etc.)
- All commits must include DCO signoff (`Signed-off-by: name <email>`)
- Tests: `pytest tests/ -v` (247 tests must pass)
- Lint: `ruff check contribai/` (must be clean)

## File Map
```
contribai/
├── core/          → config.py, models.py, middleware.py
├── analysis/      → analyzer.py, skills.py
├── agents/        → registry.py
├── tools/         → protocol.py
├── llm/           → provider.py, context.py
├── github/        → client.py, discovery.py
├── generator/     → engine.py, scorer.py
├── pr/            → manager.py, patrol.py
├── orchestrator/  → pipeline.py, memory.py
├── issues/        → solver.py
├── web/           → app.py, api.py
└── cli/           → main.py
```
