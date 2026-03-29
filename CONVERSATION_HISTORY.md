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
- **Chạy thử** `contribai target` trên repo riêng (`maptoan/MTrans`): phân tích + sinh patch **thành công**; **PR không tạo được** do GitHub PAT thiếu quyền `create reference` (403). *Why:* token cần quyền ghi nội dung/nhánh (classic `repo` hoặc fine-grained **Contents: Read and write**).

### Pending / Blockers

- Khôi phục hoặc cam kết thay đổi **`config.example.yaml`** (trên một số clone có trạng thái xóa cục bộ; README vẫn `cp config.example.yaml`).
- **PAT GitHub:** cấp đủ quyền để `POST /repos/{owner}/{repo}/git/refs` (tạo nhánh) trước khi chạy live PR trên repo của chính user.
- (Tùy chọn) Đồng bộ header phiên bản trong `docs/project-roadmap.md` / `docs/system-architecture.md` với 4.1.0.

### Next Steps (ưu tiên)

1. Rotate PAT nếu từng lộ trong chat; cập nhật `config.yaml`; chạy lại `contribai target <url>` hoặc dry-run.
2. Quyết định `config.example.yaml`: restore từ upstream hoặc commit xóa + sửa README/!HDSD.
3. Kết phiên sau: thêm mục **Phiên mới** (ngày + Completed / Pending / Next Steps).

---

## Phiên 2026-03-29 (mẫu Handover)

- **Đã làm:** Phân tích tracklog `~/.contribai/contribai.log` (404 URL `.git` lần đầu; lần hai phân tích đầy đủ; lỗi 403 khi tạo ref).
- **Chưa xong:** Mở PR tự động thành công trên `MTrans` do token.
- **Next:** Sửa quyền PAT → chạy lại; không dán token vào chat.

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
