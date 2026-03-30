# CONVERSATION_HISTORY — ContribAI

Nhật ký phiên làm việc theo giao thức trong [`! Prompt to reload project information.txt`](!%20Prompt%20to%20reload%20project%20information.txt).  
**Cách dùng:** mỗi kết phiên (Handover), nối thêm khối **Phiên YYYY-MM-DD** hoặc cập nhật các mục *Completed / Pending / Next Steps* bên dưới.

---

## Trạng tổng quan (luôn cập nhật)

### Completed (đã hoàn tất — gần đây)

- Thiết lập `config.yaml` local (GitHub + Gemini), không commit secrets.
- Cấu hình Git: `origin` → fork người dùng (`maptoan/ContribAI`), `upstream` → `tang-vu/ContribAI`.
- Thêm [`!HDSD.md`](!HDSD.md) — hướng dẫn sử dụng tiếng Việt.
- Thay thế nội dung [`CLAUDE.md`](CLAUDE.md) bằng hướng dẫn đúng cho ContribAI.
- Tạo [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md) và file nhật ký này cho protocol Reload/Handover.
- Thêm [`PROJECT_HANDOVER.md`](PROJECT_HANDOVER.md) (mục lục → `CONVERSATION_HISTORY`).
- Tạo skill **Reload / Handover / Backup** trong [`.cursor/skills/`](.cursor/skills/README.md) và [`.agent/skills/`](.agent/skills/README.md) (Cursor + Antigravity).

**Trên main (commit gần đây):**

- **Gemini key pool** + cooldown, `min_request_interval_sec`, `max_concurrent_analyzers`, `config.example.yaml` + `AGENTS.md`, test `test_key_pool.py`.
- **Handover / tài liệu:** track `!HDSD`, `CLAUDE`, `GEMINI`, `PROJECT_*`, `.cursor/`, `.agent/`; `.gitignore` bổ sung pattern secret (`.env.local`, PEM, …).
- **Analyzer findings:** định dạng chính **JSON** + parse nhiều lớp (fence, repair, fallback YAML); Gemini **`response_mime_type=application/json`** qua `LLMProvider` → `GenerateContentConfig` (commit `8c96b13`).
- **Pipeline ops / an toàn** (commit `ada6ed5`): `enforce_repo_allowlist`, `secret_scan_mode` + `patch_secret_scan`, `max_prs_per_repo_per_run`, `repo_pr_cooldown_hours`, `use_gemini_json_mode`, `ANALYZER_PARSE_FAILED`, cooldown + secret scan trên nhánh issue; test `test_patch_secret_scan`, mở rộng config/memory/discovery.

- **Chạy thử:** `contribai target` trên `maptoan/MTrans` / `mcaro-go`: sau khi sửa PAT, PR tạo được (log 201 `git/refs`). `maptoan/mcaro` + `Mcaro`: có cảnh báo parse YAML ui_ux trước đổi JSON; sau đổi JSON đã commit.

### Pending / Blockers

- (Tùy chọn) Đồng bộ header phiên bản trong `docs/project-roadmap.md` / `docs/system-architecture.md` với 4.1.0.
- (Tùy chọn) Nhánh `_hunt_issues_globally`: áp `allows_repo` khi `enforce_repo_allowlist` bật — cho thống nhất tuyệt đối với discovery (hiện issue-first có thể vào repo ngoài list nếu search issue trúng).

### Next Steps (ưu tiên)

1. `git push origin main` — local **ahead 1** với `ada6ed5` (chưa push nếu máy chưa đẩy).
2. Hunt rộng: `discovery.enforce_repo_allowlist: false` (local `config.yaml`, không commit); production: bật enforce + list + `secret_scan_mode` phù hợp.
3. Phiên sau: nối khối **Phiên YYYY-MM-DD** bên dưới.

---

## Phiên 2026-03-30 (Handover)

### Completed

- Thiết kế và **commit** luồng finding: JSON chính + parse lớp (fence / heuristic / YAML fallback) + **`response_mime_type`** cho Gemini (`8c96b13`).
- Cập nhật **`PROJECT_CONTEXT.md`** (mô tả analyzer JSON).
- Tổng hợp lại mục *Trạng tổng quan*: các commit key pool, docs/skills, JSON analyzer; loại pending đã xong (`config.example`, PAT sau khi sửa).

### Pending / Blockers

- Tuỳ chọn: đồng bộ `docs/*` với 4.1.0.

### Next Steps

- Push `main` lên `origin` nếu chưa push (`8c96b13` và các commit trước).
- Reload phiên sau: đọc `PROJECT_CONTEXT` + khối này; chạy test `pytest tests/unit/test_analyzer.py` sau thay đổi analyzer.

---

## Phiên 2026-03-29 (Handover — log PAT + pipeline ops)

### Completed (log / target trước đó)

- Phân tích tracklog `~/.contribai/contribai.log` (404 `.git` lần đầu; phân tích lần hai; 403 tạo ref khi PAT thiếu quyền).

### Completed (commit `ada6ed5`)

- **`discovery.enforce_repo_allowlist`:** tắt thì bỏ qua allowlist (hunt/target/discover); mặc định `true` giữ hành vi cũ.
- **GitHub:** `secret_scan_mode`, `max_prs_per_repo_per_run`; quét patch `contribai/orchestrator/patch_secret_scan.py` trước tạo PR (kể cả nhánh issue).
- **Pipeline:** `repo_pr_cooldown_hours`, cảnh báo live khi allowlist rỗng + enforce bật; `Memory.get_latest_pr_created_at`.
- **Analysis:** `use_gemini_json_mode`, `CodeAnalyzer` + `EventType.ANALYZER_PARSE_FAILED`; `_parse_findings` trả tuple có cờ parse fail.
- **Tests / mẫu config:** `config.example.yaml`, `test_patch_secret_scan`, mở rộng analyzer/config/memory/discovery.

### Pending / Blockers

- Issue-first hunt (`_hunt_issues_globally`) chưa lọc allowlist khi enforce bật (xem *Trạng tổng quan*).

### Next Steps

- `git push origin main`; xoay/revoke secret nếu `config.yaml` từng lộ; hunt: `enforce_repo_allowlist: false` khi muốn phạm vi rộng.

---

*(Phiên log PAT cũ: Mở PR `MTrans` cần PAT đủ quyền; không dán token vào chat.)*

---

*Mẫu nối tiếp cho phiên sau:*

```markdown
## Phiên YYYY-MM-DD

### Completed
- …

### Pending / Blockers
- …

### Next Steps
- …
```
