# Hướng dẫn sử dụng ContribAI

Tài liệu ngắn gọn để cài đặt, cấu hình và chạy **ContribAI** (agent tự động phân tích repo, tạo sửa đổi và mở Pull Request trên GitHub).

---

## 1. Yêu cầu hệ thống

- **Python 3.11 trở lên** (khớp `requires-python` trong `pyproject.toml`).
- Tài khoản **GitHub** với quyền tạo fork/PR (Personal Access Token).
- **API key** cho nhà cung cấp LLM (ví dụ Google Gemini nếu `provider: gemini`).
- Kết nối Internet ổn định.

---

## 2. Cài đặt

### Windows (PowerShell)

```powershell
cd "đường-dẫn-tới\ContribAI"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -e ".[dev]"
```

Tuỳ chọn: cài thêm nhóm phụ thuộc MCP nếu dùng MCP server:

```powershell
pip install -e ".[dev,mcp]"
```

### Linux / macOS

```bash
cd ContribAI
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
```

### Kiểm tra

```bash
contribai --version
contribai --help
```

---

## 3. Cấu hình (`config.yaml`)

1. Trong thư mục gốc dự án, tạo hoặc chỉnh sửa file **`config.yaml`** (file này thường đã được liệt kê trong `.gitignore`, **không** commit lên git).
2. Điền tối thiểu:
   - **`github.token`**: GitHub PAT đủ quyền (repo, workflow tuỳ nhu cầu).
   - **`llm.provider`**, **`llm.model`**, **`llm.api_key`**: theo nhà cung cấp bạn dùng (Gemini, OpenAI, …).
3. Có thể dùng biến môi trường thay cho một phần cấu hình (xem `AGENTS.md`): ví dụ `GITHUB_TOKEN`, `GEMINI_API_KEY`.

### Bảo mật

- **Không** chia sẻ `config.yaml` công khai, **không** dán token/API key vào chat hay ảnh chụp.
- Nếu token đã lộ, hãy **thu hồi và tạo token mới** trên GitHub / Google AI Studio (hoặc console tương ứng).
- Giới hạn an toàn: chỉnh `github.max_repos_per_run`, `github.max_prs_per_day` (hoặc tương đương trong file config) cho đến khi bạn tin tưởng hành vi của agent.

---

## 4. Chạy thử an toàn (không tạo PR thật)

Trước khi chạy production, nên xem trước:

```bash
contribai run --dry-run
```

Xem thêm `contribai hunt --help` để biết có cờ `--dry-run` hoặc chế độ tương tự cho lệnh hunt.

---

## 5. Các lệnh thường dùng

### Hunt (tự động tìm repo và đóng góp)

```bash
contribai hunt
contribai hunt --rounds 5 --delay 15    # 5 vòng, nghỉ 15 phút giữa các lần
contribai hunt --mode issues            # Ưu tiên giải quyết issue
```

### Một repo cụ thể

```bash
contribai target https://github.com/chu-so/hoc-repo
contribai solve https://github.com/chu-so/hoc-repo    # Tập trung issue mở
```

### Giám sát PR đã mở (Patrol)

```bash
contribai patrol
```

Tự động đọc review/comment và có thể đề xuất sửa/push tùy cấu hình.

### Trạng thái và dọn dẹp

```bash
contribai status
contribai stats
contribai cleanup
```

### Dashboard web

```bash
contribai serve
```

Thường truy cập qua trình duyệt tại cổng **8787** (xác nhận bằng `--help` hoặc `docs/deployment-guide.md`).

### Profile có sẵn

```bash
contribai profile security-focused
```

### Lập lịch (cron)

```bash
contribai schedule --cron "0 */6 * * *"
```

---

## 6. Docker (tuỳ chọn)

Nếu triển khai bằng container, tham chiếu:

```bash
docker compose up -d dashboard
docker compose run --rm runner run
docker compose up -d dashboard scheduler
```

Chi tiết: **`docs/deployment-guide.md`**.

---

## 7. Kiểm thử và chất lượng mã (cho dev)

```bash
pytest tests/ -v
pytest tests/ -v --cov=contribai
ruff check contribai/
ruff format contribai/
```

---

## 8. Tài liệu tham khảo trong repo

| File / thư mục | Nội dung |
|----------------|----------|
| `README.md` | Tổng quan, badge phiên bản, feature |
| `AGENTS.md` | Kiến trúc, quy ước, biến môi trường |
| `CHANGELOG.md` | Lịch sử thay đổi phiên bản |
| `docs/deployment-guide.md` | Triển khai local, Docker, gợi ý production |
| `docs/system-architecture.md` | Luồng pipeline chi tiết |
| `docs/project-roadmap.md` | Lộ trình tính năng |

---

## 9. Gợi ý thứ tự làm quen

1. Cài đặt venv + `pip install -e ".[dev]"`.
2. Hoàn thiện `config.yaml`, kiểm tra token/API key.
3. Chạy `contribai run --dry-run`.
4. Thử `contribai target` trên **một repo nhỏ** hoặc fork của bạn.
5. Tăng dần hunt (`contribai hunt`) và bật dashboard nếu cần theo dõi.

---

*Tài liệu này là bản hướng dẫn sử dụng cục bộ; phiên bản ứng dụng lấy theo `contribai --version` hoặc `pyproject.toml`.*
