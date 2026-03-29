# ContribAI — Hướng dẫn bắt buộc cho Antigravity / Gemini (dự án)

File này **bắt buộc** agent tuân thủ trong mọi phiên làm việc trên repo này, cùng với [`AGENTS.md`](AGENTS.md) và [`CLAUDE.md`](CLAUDE.md). Thứ tự ưu tiên khi mâu thuẫn: **CHANGELOG.md** + **AGENTS.md** hơn tài liệu `docs/` cũ.

---

## 1. Đọc trước khi sửa

- [`CLAUDE.md`](CLAUDE.md) — điểm vào module, quy tắc repo, skills Reload/Handover/Backup.
- [`AGENTS.md`](AGENTS.md) — định nghĩa sản phẩm, pipeline, conventions đầy đủ, env vars, limitations.

Khi cần ngữ cảnh phiên: [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md), [`CONVERSATION_HISTORY.md`](CONVERSATION_HISTORY.md).

---

## 2. Chuẩn code (bắt buộc)

- Python **3.11+**; `snake_case` / `PascalCase`; docstring kiểu **Google**.
- **Mọi I/O bất đồng bộ** (`async`/`await`). Không `bare except`.
- Imports tuyệt đối; `from __future__ import annotations`; type hints đầy đủ (`str | None`).
- **100** ký tự/dòng tối đa; **`ruff format`** / **`ruff check`** trên `contribai/`.
- **LLM:** qua provider `complete()` đã có trong codebase.
- **GitHub:** qua **`GitHubClient`**, không tự gọi API rời trong luồng chính.

---

## 3. Cấm sửa

`LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/FUNDING.yml` và file meta governance tương tự.

Không lộ / commit `config.yaml`, token, secrets.

---

## 4. Xác minh

Sau thay đổi logic đáng kể:

```bash
pytest tests/ -q
ruff check contribai/
ruff format contribai/
```

Backup stable (trước refactor lớn): xem skill **`protocol-backup`** trong [`.agent/skills/protocol-backup/SKILL.md`](.agent/skills/protocol-backup/SKILL.md) — dùng **`contribai run --dry-run`** và/hoặc **`pytest`**, không `python main.py`.

---

## 5. Protocol phiên (skills)

| Lệnh user | Thư mục |
|-----------|---------|
| Reload | `.agent/skills/protocol-reload/` |
| Handover | `.agent/skills/protocol-handover/` |
| Backup | `.agent/skills/protocol-backup/` |

Thực hiện **đủ** các bước trong `SKILL.md` tương ứng. Nguồn gốc prompt: [`! Prompt to reload project information.txt`](!%20Prompt%20to%20reload%20project%20information.txt).

Có thể copy các folder skill vào `~/.gemini/skills/` nếu Antigravity chỉ load global ([codelab](https://codelabs.developers.google.com/getting-started-with-antigravity-skills)).

---

## 6. Ngôn ngữ

User tiếng Việt → trả lời tiếng Việt; code và identifier giữ nguyên.
