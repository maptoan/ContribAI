---
name: protocol-reload
description: >-
  Runs the project Reload protocol at session start. Use when the user says Reload,
  /reload, đồng bộ ngữ cảnh, khởi động phiên, sync project context, or opens a
  new work session for this repository. Reads context files and CHANGELOG; outputs
  Ready summary (Current State, WIP, priority actions).
---

# Protocol: Reload (khởi động phiên)

**Nguồn gốc:** [`! Prompt to reload project information.txt`](../../../!%20Prompt%20to%20reload%20project%20information.txt) §1.

## Khi kích hoạt

User gọi **Reload** (hoặc tương đương). Thực hiện **đủ các bước** dưới đây trước khi bàn luận code mới.

## Bước 1 — Phân tích kiến trúc

Đọc và tóm tắt nội dung cốt lõi:

- [`PROJECT_CONTEXT.md`](../../../PROJECT_CONTEXT.md) — stack, workflow, cấu trúc thư mục
- [`PROJECT_HANDOVER.md`](../../../PROJECT_HANDOVER.md) — mục lục bàn giao; chi tiết trong `CONVERSATION_HISTORY.md`
- [`AGENTS.md`](../../../AGENTS.md) — nếu cần chi tiết module/quy ước (repo ContribAI)

## Bước 2 — Truy vết lịch sử

Đọc [`CONVERSATION_HISTORY.md`](../../../CONVERSATION_HISTORY.md):

- Việc vừa hoàn thành (**Completed**)
- **The Why** — lý do thay đổi logic nếu có ghi
- **Pending / Blockers**

## Bước 3 — Kiểm tra tiến độ

Rà [`CHANGELOG.md`](../../../CHANGELOG.md) — các mục phiên bản gần nhất và `[Unreleased]` (nếu có).

## Kết quả bắt buộc (đầu ra cho user)

Xác nhận trạng thái **Ready** bằng **một** bản tóm tắt súc tích gồm:

1. **Current State** — trạng thái hiện tại của dự án / phiên bản / nhánh chính (nếu biết từ ngữ cảnh).
2. **Work in Progress** — tác vụ dang dở hoặc blocker.
3. **Đề xuất hành động ưu tiên** — 2–5 mục cho phiên này.

Ngôn ngữ trả lời: **tiếng Việt** (trừ khi user yêu cầu khác).

## Lưu ý

- Không cần sửa file trừ khi user yêu cầu; Reload chủ yếu **đọc + tóm tắt**.
- Repo này là **ContribAI** (Python). Không nhầm với template generic khác.
