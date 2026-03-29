---
name: protocol-backup
description: >-
  Runs pre-large-change Backup Stable protocol: verify tests/dry-run, git commit and
  annotated tag, optional copy backup, CHANGELOG checkpoint. Use when the user says
  Backup, /backup, stable checkpoint, backup trước refactor, or before major
  architectural change.
---

# Protocol: Backup Stable (trước thay đổi lớn)

**Nguồn gốc:** [`! Prompt to reload project information.txt`](../../../!%20Prompt%20to%20reload%20project%20information.txt) §3.

**Điều chỉnh cho repo ContribAI:** Không có `python main.py`. Dùng `pytest` và/hoặc `contribai run --dry-run`.

## Khi kích hoạt

User gọi **Backup** (checkpoint ổn định trước refactor lớn).

## Bước 1 — Xác nhận stable

Trong thư mục gốc repo, chạy **ít nhất một** trong các lệnh (ưu tiên cả hai nếu môi trường đủ):

```bash
pytest tests/ -q
contribai run --dry-run
```

- Nếu **lỗi** → **DỪNG**: báo user sửa trước, **không** tạo tag.
- Ghi lại **kết quả** (pass / fail, stderr ngắn nếu fail).

## Bước 2 — Git commit + tag chú thích

Chỉ khi bước 1 pass và user **đồng ý** git thay đổi (hoặc user đã yêu cầu rõ chạy backup):

1. Kiểm tra `git status` — không commit file nhạy cảm (`config.yaml` đã `.gitignore`).
2. Hướng dẫn hoặc thực hiện (theo user):

```bash
git add -A
git commit -m "chore: stable checkpoint before [mô tả thay đổi]"
git tag -a stable-vX.Y-pre-[tên-thay-đổi] -m "Stable checkpoint trước khi [mô tả]"
```

- `.` và `X.Y` lấy từ `pyproject.toml` hoặc ý user.

## Bước 3 — Backup vật lý (tùy chọn)

- Nếu có `scripts/backup_to_nas.py` và đã cấu hình → có thể chạy.
- Nếu không: có thể copy thủ công thư mục quan trọng (ví dụ `contribai/`) sang `backups/contribai_stable_YYYYMMDD/` **chỉ khi user yêu cầu**.

## Bước 4 — Ghi nhận CHANGELOG

Thêm **một dòng** vào đầu section [`CHANGELOG.md`](../../../CHANGELOG.md) `## [Unreleased]` (tạo section nếu chưa có):

```markdown
- Checkpoint: stable-vX.Y trước khi [tên thay đổi] ([hash ngắn nếu có])
```

Hoặc mô tả một dòng tương đương theo Keep a Changelog.

## Kết quả bắt buộc (báo cáo cho user)

1. **Tên tag** (nếu đã tạo) hoặc “chưa tạo — lý do”.
2. **Hash commit** của checkpoint (nếu có).
3. **Kết quả kiểm tra ổn định** (pytest / dry-run).

Ngôn ngữ: **tiếng Việt**.

## Lưu ý

- Tag/commit là thao tác **mang tính phá hủy nhẹ** trên lịch sử làm việc — luôn xác nhận với user nếu có nghi ngờ.
- Không force-push trừ khi user yêu cầu rõ.
