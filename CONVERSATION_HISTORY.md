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

- **Chạy thử:** `contribai target` trên `maptoan/MTrans` / `mcaro-go`: sau khi sửa PAT, PR tạo được (log 201 `git/refs`). `maptoan/mcaro` + `Mcaro`: có cảnh báo parse YAML ui_ux trước đổi JSON; sau đổi JSON đã commit.

### Pending / Blockers

- (Tùy chọn) Đồng bộ header phiên bản trong `docs/project-roadmap.md` / `docs/system-architecture.md` với 4.1.0.
- Nếu model Gemini preview không hỗ trợ tốt JSON mode: cân nhắc **cờ config** tắt `application/json` cho analyzer (chưa có trong `config.yaml`).

### Next Steps (ưu tiên)

1. `git pull` / `git push` fork nếu làm việc đa máy; đồng bộ `upstream` khi cần.
2. Chạy lại `contribai target` / `contribai serve` sau khi merge JSON analyzer; theo dõi log nếu API trả 400 do JSON mode + model lạ.
3. Phiên sau: nối khối **Phiên YYYY-MM-DD** bên dưới.

---

## Phiên 2026-03-29 (mẫu Handover)

- **Đã làm:** Phân tích tracklog `~/.contribai/contribai.log` (404 URL `.git` lần đầu; lần hai phân tích đầy đủ; lỗi 403 khi tạo ref).
- **Chưa xong:** Mở PR tự động thành công trên `MTrans` do token.
- **Next:** Sửa quyền PAT → chạy lại; không dán token vào chat.

---

## Phiên 2026-03-30 (Handover)

### Completed

- Thiết kế và **commit** luồng finding: JSON chính + parse lớp (fence / heuristic / YAML fallback) + **`response_mime_type`** cho Gemini (`8c96b13`).
- Cập nhật **`PROJECT_CONTEXT.md`** (mô tả analyzer JSON).
- Tổng hợp lại mục *Trạng tổng quan*: các commit key pool, docs/skills, JSON analyzer; loại pending đã xong (`config.example`, PAT sau khi sửa).

### Pending / Blockers

- Tuỳ chọn: cờ cấu hình tắt JSON mode analyzer nếu model/API lỗi.
- Tuỳ chọn: đồng bộ `docs/*` với 4.1.0.

### Next Steps

- Push `main` lên `origin` nếu chưa push (`8c96b13` và các commit trước).
- Reload phiên sau: đọc `PROJECT_CONTEXT` + khối này; chạy test `pytest tests/unit/test_analyzer.py` sau thay đổi analyzer.

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
