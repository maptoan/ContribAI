---
name: protocol-handover
description: >-
  Runs the session-end Handover protocol: update CONVERSATION_HISTORY and optionally
  PROJECT_CONTEXT. Use when the user says Handover, /handover, kết phiên, bàn giao,
  end session snapshot, or save context for next session.
---

# Protocol: Handover (kết phiên)

**Nguồn gốc:** [`! Prompt to reload project information.txt`](../../../!%20Prompt%20to%20reload%20project%20information.txt) §2.

## Khi kích hoạt

User gọi **Handover**. Phải **ghi lại** ngữ cảnh để phiên sau tiếp tục được.

## Bước 1 — Tổng hợp

Đúc kết **phiên hiện tại** (từ hội thoại + diff/git nếu cần):

- Thay đổi code / file quan trọng
- Bug fix
- Quyết định kiến trúc

## Bước 2 — Cập nhật nhật ký

Sửa [`CONVERSATION_HISTORY.md`](../../../CONVERSATION_HISTORY.md):

1. Cập nhật mục **Trạng tổng quan** — **Completed**, **Pending / Blockers**, **Next Steps** cho đúng thực tế.
2. **Nối** khối mới theo mẫu (đổi ngày):

```markdown
## Phiên YYYY-MM-DD

### Completed
- …

### Pending / Blockers
- …

### Next Steps
- …
```

Giữ mạch lịch sử: phiên mới ở **cuối file** hoặc ngay sau template — thống nhất một cách trong repo (ưu tiên: sau *Trạng tổng quan*, trước hoặc sau các phiên cũ; repo hiện nối phiên dưới mục tổng quan).

## Bước 3 — Đồng bộ PROJECT_CONTEXT

Nếu có thay đổi **cấu trúc thư mục**, **entry point**, **stack**, **remote Git**, hoặc **quy ước làm việc**: cập nhật [`PROJECT_CONTEXT.md`](../../../PROJECT_CONTEXT.md) tương ứng.

Cập nhật [`PROJECT_HANDOVER.md`](../../../PROJECT_HANDOVER.md) **chỉ** nếu muốn thêm một dòng “xem phiên ZZZ” — không bắt buộc; chi tiết vẫn ở `CONVERSATION_HISTORY.md`.

## Kết quả bắt buộc

- Xác nhận với user: **`CONVERSATION_HISTORY.md` đã được cập nhật** (và `PROJECT_CONTEXT.md` nếu đã sửa).
- Ngắn gọn: 3–7 bullet về những gì đã ghi.

Ngôn ngữ: **tiếng Việt** (trừ khi user yêu cầu khác).

## Lưu ý

- Không commit git trừ khi user yêu cầu.
- Không ghi secret (token, API key) vào markdown.
