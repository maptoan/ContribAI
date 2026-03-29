# PROJECT_CONTEXT — ContribAI

**Mục đích:** Ảnh chụp ngữ cảnh dự án cho bước **Reload** trong [`! Prompt to reload project information.txt`](!%20Prompt%20to%20reload%20project%20information.txt). Cập nhật khi đổi kiến trúc, entry point, hoặc quy ước làm việc.

**Phiên bản ứng dụng (tham chiếu):** 4.1.0 (`pyproject.toml`).  
**Cập nhật lần cuối:** 2026-03-29

---

## 1. Bản chất sản phẩm

- **ContribAI:** agent Python **tự động** tìm repo GitHub, phân tích mã, sinh sửa đổi, mở PR, giám sát CI/patrol.
- **Không phải** SDK hay app web cho người dùng cuối; là **công cụ vận hành** trên repo ngoài.

---

## 2. Tech stack

| Lớp | Công nghệ |
|-----|-----------|
| Ngôn ngữ | Python ≥ 3.11 |
| Bất đồng bộ | asyncio, httpx |
| DB | SQLite (aiosqlite), memory tại `~/.contribai/` (hoặc theo `config`) |
| LLM | Gemini (mặc định thường dùng), OpenAI, Anthropic, Ollama, Vertex |
| GitHub | REST v3 qua client nội bộ |
| Web / dashboard | FastAPI, uvicorn (~8787) |
| CLI | Typer / Click + Rich |
| Test / lint | pytest (~400+), ruff |

Chi tiết: [`AGENTS.md`](AGENTS.md).

---

## 3. Luồng xử lý (workflow)

```
Discovery → Middleware chain → Analysis (skills + analyzers) → Generation → PR → CI / Patrol
```

- **Middleware:** rate limit, validation, retry, DCO, quality gate (`contribai/core/middleware.py`).
- **Phân tích:** `contribai/analysis/` — progressive skills, repo intelligence (v4+).
- **Sinh mã:** `contribai/generator/engine.py`, scorer.
- **PR:** `contribai/pr/manager.py`; phản hồi review: `patrol.py`.

---

## 4. Cấu trúc thư mục (cấp cao)

```
contribai/          # Mã nguồn chính (core, github, analysis, generator, orchestrator, pr, …)
tests/              # pytest
docs/               # Kiến trúc, roadmap, deployment, …
plans/reports/      # Báo cáo agent (tuỳ phiên)
scripts/            # Tiện ích
.github/            # CI, template
```

Entry CLI: `contribai` → `contribai.cli.main`. Cấu hình: `config.yaml` (local, gitignored).

---

## 5. Tài liệu nội bộ (bản đồ đọc nhanh)

| File | Vai trò |
|------|---------|
| `AGENTS.md` | Hướng dẫn AI đầy đủ |
| `CLAUDE.md` | Gợi ý riêng cho Claude |
| `GEMINI.md` | Quy tắc bắt buộc cho Antigravity / Gemini (gốc repo) |
| `.cursor/rules/contribai-mandatory.mdc` | Quy tắc Cursor `alwaysApply` |
| `!HDSD.md` | Hướng dẫn sử dụng tiếng Việt |
| `CHANGELOG.md` | Lịch sử release |
| `CONVERSATION_HISTORY.md` | Nhật ký phiên / blocker / next steps |
| `README.md` | Giới thiệu public |

---

## 6. Remote Git (workspace fork)

- **`origin`:** fork người dùng (ví dụ `maptoan/ContribAI`).
- **`upstream`:** `tang-vu/ContribAI` (đồng bộ khi cần).

---

## 7. Chạy thử & log vận hành

- Log file: `%USERPROFILE%\.contribai\contribai.log`
- Sự kiện JSONL: `%USERPROFILE%\.contribai\events.jsonl` (cạnh `memory.db` theo config)

---

## 8. Handover vs prompt reload

**[`PROJECT_HANDOVER.md`](PROJECT_HANDOVER.md)** là mục lục trỏ tới chi tiết trong **[`CONVERSATION_HISTORY.md`](CONVERSATION_HISTORY.md)**. Skill **Reload** đọc cả hai theo [`! Prompt to reload project information.txt`](!%20Prompt%20to%20reload%20project%20information.txt).

**Skills (Cursor / Antigravity):** `.cursor/skills/protocol-{reload,handover,backup}/` và `.agent/skills/` (xem `README` trong từng thư mục).
