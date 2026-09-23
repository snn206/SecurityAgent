# SecurityAgent

A modular, multi-agent system for automated security research, penetration testing, and continuous security intelligence.
Built on **LangGraph**, **Deep Agents**, a **JEV (Judge / Evaluator / Verifier) Harness**, an **Embedded NoSQL Document Store**, and a **10-Agent Hierarchical Brain**.

---

## Features

- **10-Agent Hierarchical Brain** — 1 Grandparent Coordinator ("Ông"), 3 Parent Specialist Leads ("Cha"), and up to 2 Child Workers per Parent ("Con") strictly bounded to <= 10 agents.
- **Parent Task Queue** — Asynchronous priority queue that buffers and dispatches tasks when tasks > 3 (number of parent slots).
- **JEV Harness & Evolution** — Evaluator, Verifier, and Judge loop with continuous learning ("rút kinh nghiệm") and distilled strategy evolution.
- **Dual Storage Layer** — SQLite (via SQLAlchemy & aiosqlite for relational traces and checkpoints) + Embedded NoSQL Document Store (zero-install MongoDB-like document database).
- **User Memory Management** — Web UI & REST API for inspecting, editing, deleting agent memories, and injecting human "Golden Rules".
- **Provider Abstraction** — Hot-swap between Anthropic (Claude), OpenAI, Ollama (Local), DeepSeek, Qwen, Mistral, NVIDIA NIM, and Mock without code modifications.
- **Isolated Kali Sandbox** — All tool execution happens strictly inside Docker (Kali Linux container), never on the host.
- **Real-Time Telemetry** — WebSocket (`/ws/{id}`) & SSE (`/stream/{id}`) event streams.
- **Clean React UI** — Minimalist cybersecurity dashboard with zero generic icons/emojis, pure typographic indicators, and high-density telemetry.

---

## Hướng Dẫn Cài Đặt & Chạy Hệ Thống (Quick Start)

### 1. Yêu Cầu Môi Trường (Prerequisites)
- **Hệ điều hành**: Linux / WSL2 (Ubuntu / Kali Linux) / macOS
- **Python**: `>= 3.11`
- **Node.js**: `>= 20.x` (dành cho build giao diện React)
- **Docker**: Dành cho sandbox Kali Linux cô lập
- **Trình quản lý gói**: [uv](https://docs.astral.sh/uv/) (khuyên dùng) hoặc `pip`

---

### 2. Cài Đặt (Installation)

#### Cách 1: Cài Đặt Trực Tiếp Từ GitHub (Khuyên Dùng Cho Người Sử Dụng)
Bạn có thể cài đặt trực tiếp `SecurityAgent` từ GitHub bằng `uv` hoặc `pip` mà không cần clone toàn bộ repository:

```bash
# Cài đặt bản mới nhất qua uv (dùng giao thức SSH):
uv pip install git+ssh://git@github.com/snn206/SecurityAgent.git

# Hoặc qua HTTPS:
uv pip install git+https://github.com/snn206/SecurityAgent.git

# Cài đặt qua pip tiêu chuẩn:
pip install git+ssh://git@github.com/snn206/SecurityAgent.git
# Hoặc: pip install git+https://github.com/snn206/SecurityAgent.git

# Cài đặt kèm các optional dependencies (ví dụ xuất báo cáo PDF và công cụ dev):
uv pip install "security-agent[pdf,dev] @ git+https://github.com/snn206/SecurityAgent.git"
```

##### Cài Đặt & Ghim Phiên Bản Cụ Thể (Version Pinning & Rollback từ Git)
Bạn có thể cài đặt bất kỳ phiên bản nào theo **Git Tag** hoặc **Commit SHA** cụ thể:
```bash
# Cài đặt theo Git Release Tag (ví dụ v0.1.0):
uv pip install git+https://github.com/snn206/SecurityAgent.git@v0.1.0

# Rollback hoặc cài đặt theo Commit SHA cụ thể:
uv pip install git+https://github.com/snn206/SecurityAgent.git@e312112

# Cài đặt theo Branch (ví dụ nhánh develop hoặc main):
uv pip install git+https://github.com/snn206/SecurityAgent.git@main
```

Sau khi cài đặt, hai lệnh CLI sẽ sẵn sàng trong terminal:
- `security-agent` — Khởi chạy API Server và Web UI.
- `sa-update` — Quản lý, kiểm tra, update và rollback phiên bản từng thành phần độc lập.

---

#### Cách 2: Clone Mã Nguồn (Dành Cho Phát Triển Cục Bộ)
```bash
# 1. Clone repository
git clone git@github.com:snn206/SecurityAgent.git
cd SecurityAgent

# 2. Thiết lập biến môi trường
cp .env.example .env

# 3. Cài đặt môi trường bằng uv (tự động tạo .venv và cài đặt trọn gói)
uv sync --extra dev

# Hoặc kích hoạt venv và cài đặt bằng pip:
source .venv/bin/activate
pip install -e ".[dev,pdf]"
```

---

### 3. Build Giao Diện React UI (Đã Build Sẵn Trong Repo)

> [!NOTE]
> Bản build production của React UI đã được biên dịch sẵn tại `src/security_agent/ui/dist/`.
> Nếu bạn chỉnh sửa mã nguồn React trong `src/security_agent/ui/src/`, hãy chạy lệnh sau để build lại:

```bash
make ui-build
# Hoặc thủ công:
cd src/security_agent/ui && npm install && npm run build && cd ../../..
```

---

### 4. Build Docker Sandbox (Tùy Chọn Khi Muốn Chạy Tool Thực Tế)

Để chạy các công cụ (Nmap, Gobuster, Nikto, Nuclei, SQLMap) trong môi trường Kali Linux cô lập:

```bash
make sandbox-build
# Hoặc: docker build -f docker/Dockerfile.sandbox -t security-agent-sandbox:latest docker/
```

---

### 5. Khởi Chạy Hệ Thống (Running SecurityAgent)

#### Cách 1: Chạy Chế Độ Phát Triển (Khuyên Dùng)
Chạy server FastAPI (tự động phục vụ cả REST API, WebSocket và Giao diện React UI):

```bash
make dev
# Hoặc:
uv run uvicorn security_agent.api.app:create_app --factory --host 0.0.0.0 --port 8080 --reload
```

Sau khi chạy, mở trình duyệt:
- **Giao diện Web UI**: [http://localhost:8080](http://localhost:8080)
- **Tài liệu API Swagger**: [http://localhost:8080/api/docs](http://localhost:8080/api/docs)
- **Tài liệu ReDoc**: [http://localhost:8080/api/redoc](http://localhost:8080/api/redoc)
- **Kiểm tra trạng thái**: [http://localhost:8080/api/v1/health](http://localhost:8080/api/v1/health)

#### Cách 2: Chạy Giao Diện React Dev Server (Hot-Reload Giao Diện)
Nếu bạn đang phát triển giao diện UI và muốn hot-reload trực tiếp:

```bash
make ui-dev
# Giao diện Vite dev server chạy tại http://localhost:5173 và tự động proxy API sang port 8080
```

#### Cách 3: Chạy Toàn Bộ Bằng Docker Compose
Khởi động trọn gói API server + Docker sandbox + database:

```bash
make docker-up
# Dừng hệ thống:
make docker-down
```

---

## Cấu Trúc Não Bộ 10 Agent (1-3-2 Topology)

Hệ thống điều phối tối đa **10 Agent** cùng phối hợp giải quyết nhiệm vụ:

```
[GRANDPARENT COORDINATOR (Ông)] (1 Agent)
  │  Nhận nhiệm vụ, phân rã mục tiêu, điều phối toàn cục, giám sát vòng lặp JEV
  ▼
[PARENT DOMAIN LEADS (Cha)] (Tối đa 3 Agent) ── [TASK QUEUE (Nếu > 3 task)]
  ├── Parent 1: Recon Lead (Trinh sát & Dò quét bề mặt mạng)
  ├── Parent 2: Vulnerability Lead (Rà quét lỗ hổng & Kiểm tra cấu hình)
  └── Parent 3: Exploit Lead (Kiểm chứng PoC an toàn trong Sandbox)
        │
        ▼
[CHILD SPECIALIST WORKERS (Con)] (Mỗi Cha sinh tối đa 2 Con = 6 Con)
  ├── Con của Recon: Port Scanner Worker (Nmap) & Subdomain Worker (Gobuster)
  ├── Con của Vuln: Template Matcher (Nuclei) & Web Auditor (Nikto)
  └── Con của Exploit: PoC Verifier (Sandbox) & Payload Tester (SQLMap)
```

---

## Quản Lý Bộ Nhớ Agent (Agent Memory Management)

Người dùng có toàn quyền quản lý bộ nhớ agent qua REST API hoặc trên Tab **MEMORY & BRAIN** của Web UI:
- **JEV Lessons Learned**: Các bài học do hệ thống tự học từ các lần chạy trước (ví dụ: phát hiện WAF, tinh chỉnh timing flags).
- **User Golden Rules**: Các quy tắc vàng do người dùng trực tiếp nạp vào (ví dụ: cấm quét subnet nhạy cảm, ép dùng stealth scan).
- **Target Knowledge**: Hồ sơ tri thức tích lũy về các mục tiêu qua thời gian.

REST API:
- `GET /api/v1/memory?collection=golden_rules` — Xem danh sách bộ nhớ
- `POST /api/v1/memory` — Nạp thêm chỉ thị / Golden Rule mới
- `PUT /api/v1/memory/{collection}/{id}` — Chỉnh sửa / đính chính tri thức
- `DELETE /api/v1/memory/{collection}/{id}` — Xóa / quên tri thức lỗi thời
- `POST /api/v1/memory/reset` — Reset toàn bộ bộ nhớ

---

## Chạy Kiểm Thử Tự Động (Tests)

Toàn bộ hệ thống đi kèm 42 bài kiểm thử (Unit test + Integration test):

```bash
# Chạy toàn bộ test suite
make test
# Hoặc:
uv run pytest tests/ -v

# Chạy test nhanh các thành phần cốt lõi
uv run python scripts/run_unit_tests.py
```

---

## Quản Lý Phiên Bản Độc Lập (Versioning CLI: `sa-update`)

Hệ thống tuân thủ nghiêm ngặt nguyên tắc **độc lập phiên bản**:
- Các thành phần (`core`, `providers`, `agents`, `tools`, `packages`, `extensions`) có version riêng, **không khóa version chéo**.
- Có thể **update/rollback từng thành phần độc lập** mà không ảnh hưởng tới thành phần khác.
- Có lệnh **update toàn bộ lên latest**.
- Hỗ trợ đa dạng loại artifact: `git-tag`, `git-commit`, `docker-tag`, `pypi`, `.zip`.
- Quản lý metadata phiên bản tập trung tại [`registry/versions.yaml`](file:///home/nexus/documents/security-agent/registry/versions.yaml) kèm changelog chi tiết.

### 1. Bảng Lệnh CLI `sa-update`

```bash
# ── Xem danh sách & thông tin ──────────────────────────────────────────────
sa-update list                              # Liệt kê tất cả component, version và artifact type
sa-update info core                         # Xem chi tiết metadata, ref, changelog của core
sa-update info providers.anthropic          # Xem chi tiết package và min-version provider

# ── Cập nhật (Update) ──────────────────────────────────────────────────────
sa-update update all                        # Cập nhật TOÀN BỘ thành phần lên bản mới nhất
sa-update update core                       # Cập nhật riêng core từ GitHub repo (HTTPS)
sa-update update core --ssh                 # Cập nhật riêng core từ GitHub repo (SSH)
sa-update update providers.anthropic        # Cập nhật độc lập provider Anthropic
sa-update update tools.nmap                 # Cập nhật độc lập tool Nmap trong Kali sandbox

# ── Quay lui phiên bản (Rollback) ──────────────────────────────────────────
# Rollback core về Git Release Tag cụ thể:
sa-update rollback core v0.1.0

# Rollback core về Commit SHA cụ thể:
sa-update rollback core e312112

# Rollback độc lập một provider về phiên bản thư viện chỉ định:
sa-update rollback providers.anthropic 0.2.0

# Rollback phiên bản tool trong registry:
sa-update rollback tools.nmap 7.94
```

### 2. Dùng Makefile (Khi đang ở thư mục repo)

```bash
make versions                                          # Chạy sa-update list
make update                                            # Cập nhật toàn bộ lên latest
make update-component COMPONENT=core                   # Cập nhật riêng core
make update-component COMPONENT=tools.nmap             # Cập nhật riêng 1 tool
make rollback COMPONENT=providers.anthropic VERSION=0.2.0  # Rollback phiên bản
```

---

## Cấu Hình GraphCode MCP Trong WSL

Nếu bạn sử dụng GraphCode để phân tích đồ thị mã nguồn, thêm cấu hình sau vào `~/.gemini/config/mcp_config.json`:

```json
{
  "mcpServers": {
    "graphcode": {
      "command": "/home/nexus/.nvm/versions/node/v20.20.2/bin/node",
      "args": [
        "/home/nexus/.nvm/versions/node/v20.20.2/bin/graphcode",
        "mcp"
      ],
      "env": {
        "PATH": "/home/nexus/.nvm/versions/node/v20.20.2/bin:/usr/local/bin:/usr/bin:/bin"
      }
    }
  }
}
```
