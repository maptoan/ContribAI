# Hướng dẫn cho Claude (ContribAI)

Tài liệu này bổ sung cho [`AGENTS.md`](AGENTS.md) khi bạn là **Claude** (Claude Code, Cursor, v.v.) làm việc trong repo **ContribAI** — agent Python tự động đóng góp PR trên GitHub.

---

## 1. Đọc gì trước khi sửa code

1. **[`AGENTS.md`](AGENTS.md)** — định nghĩa dự án, stack, pipeline, graph module, quy ước, env vars, giới hạn.
2. **[`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md)** — ảnh chụp ngữ cảnh và cấu trúc cho phiên làm việc.
3. **[`CONVERSATION_HISTORY.md`](CONVERSATION_HISTORY.md)** — việc đã làm, blocker, bước tiếp theo.
4. **[`CHANGELOG.md`](CHANGELOG.md)** — thay đổi theo phiên bản.

Hướng dẫn chạy cục bộ (tiếng Việt): [`!HDSD.md`](!HDSD.md).

---

## 2. ContribAI là gì (một dòng)

**Agent tự động** (Python 3.11+): discovery → middleware → phân tích (skills + LLM) → sinh patch → PR/patrol — **không phải** thư viện UI cho end-user.

Luồng cốt lõi:

`Discovery → Middleware → Analysis → Generation → PR → CI monitor`

---

## 3. Điểm vào quan trọng

| Khu vực | File / module |
|---------|----------------|
| CLI | `contribai/cli/main.py` |
| Pipeline | `contribai/orchestrator/pipeline.py` |
| Cấu hình | `contribai/core/config.py` |
| GitHub API | `contribai/github/client.py` |
| Phân tích | `contribai/analysis/analyzer.py`, `skills.py` |
| Sinh mã | `contribai/generator/engine.py` |
| PR | `contribai/pr/manager.py`, `patrol.py` |
| Sự kiện / log | `contribai/core/events.py` (JSONL cạnh `memory.db`) |
| MCP | `contribai/mcp_server.py` |

---

## 4. Quy tắc khi chỉnh sửa (bắt buộc tuân theo repo)

- Chỉ sửa **mã nguồn** cần thiết; khớp style hiện có (`snake_case`, type hints, async I/O, Google docstrings).
- **Không** sửa: `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/FUNDING.yml` và meta governance tương tự (theo `AGENTS.md`).
- Agent khi chạy **bỏ qua** sửa đổi trực tiếp nhiều loại `.md`/`.yaml`/`.json` trên repo **đích**; trong **repo ContribAI** thì vẫn có thể cập nhật docs nếu người dùng yêu cầu rõ.
- LLM: `await provider.complete(...)`; GitHub: qua `GitHubClient`.
- Kiểm tra: `pytest tests/ -q`, `ruff check contribai/`, `ruff format contribai/`.

Config cục bộ: `config.yaml` (không commit; đã `.gitignore`).

---

## 5. Tiết kiệm token khi explore

- Ưu tiên `grep`/đọc **một** module liên quan thay vì đọc cả tree.
- Module lớn: đọc phần đầu file + hàm được grep trỏ tới.

---

## 6. Giao thức Reload / Handover / Backup (skills)

- **Nguồn:** [`! Prompt to reload project information.txt`](!%20Prompt%20to%20reload%20project%20information.txt)
- **Cursor:** `.cursor/skills/` — `protocol-reload`, `protocol-handover`, `protocol-backup` (gọi ngắn: **Reload**, **Handover**, **Backup**).
- **Antigravity:** `.agent/skills/` — cùng nội dung `SKILL.md`; có thể copy sang `~/.gemini/antigravity/skills/` nếu dùng global ([codelab Antigravity Skills](https://codelabs.developers.google.com/getting-started-with-antigravity-skills)).
- Reload đọc `PROJECT_CONTEXT.md`, `PROJECT_HANDOVER.md`, `CONVERSATION_HISTORY.md`, `CHANGELOG.md`.

---

## 7. Phiên bản

Đồng bộ với `pyproject.toml` / `contribai --version` (ví dụ **4.1.0**). Nếu mâu thuẫn với tài liệu cũ trong `docs/`, ưu tiên **CHANGELOG + AGENTS.md**.

---

## 8. Thiết lập IDE — quy tắc bắt buộc mọi phiên

Để agent **luôn** tuân thủ chuẩn và quy trình trong file này + `AGENTS.md`:

| Công cụ | File | Ghi chú |
|---------|------|--------|
| **Cursor** | [`.cursor/rules/contribai-mandatory.mdc`](.cursor/rules/contribai-mandatory.mdc) | `alwaysApply: true` — áp dụng mọi hội thoại trong workspace. |
| **Antigravity / Gemini** | [`GEMINI.md`](GEMINI.md) ở gốc repo | Bắt buộc đọc cùng `CLAUDE.md` / `AGENTS.md`; skills trong `.agent/skills/`. |

Nếu IDE không nhận rule, mở đúng **thư mục gốc** repo ContribAI và kiểm tra cài đặt Agent / Project instructions của từng IDE.
