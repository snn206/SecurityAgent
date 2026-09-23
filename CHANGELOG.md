# SecurityAgent — Component Changelog

Tài liệu ghi lại toàn bộ lịch sử phiên bản của từng thành phần trong hệ thống SecurityAgent.
Các thành phần có **phiên bản độc lập**, được phân tách thành từng phần riêng biệt, không viết lẫn lộn.

Tuân thủ chuẩn [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) và [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## 1. System Core & Architecture (`core`)

### [0.1.0] — 2026-09-23
- **Artifact**: `git-tag` (`v0.1.0`) | `git-commit` (`463a2e6`)
- **Mô tả**: Bộ khung điều phối trung tâm LangGraph, JEV Harness, và hệ thống lưu trữ kép.
- **Thay đổi**:
  - Khởi tạo kiến trúc đồ thị trạng thái LangGraph (`StateGraph`, `AgentState`, `Checkpointer`).
  - Tích hợp vòng lặp JEV (`Verifier`, `Evaluator`, `Judge`) phục vụ đánh giá và tiến hóa tri thức.
  - Xây dựng tầng lưu trữ kép: SQLite (aiosqlite) cho checkpoint/lịch sử + TinyDB NoSQL cho memory.
  - Xây dựng FastAPI REST API (port 8080), WebSocket `/ws/{id}` và SSE `/stream/{id}`.
  - Đóng gói Giao diện Web React vào thư mục `src/security_agent/ui/dist`.
  - Hỗ trợ cài đặt trực tiếp từ GitHub qua `uv` / `pip` và CLI `sa-update`.

---

## 2. Agent Providers (`providers.*`)

### `providers.anthropic`
#### [0.1.0] — 2026-09-23
- **Artifact**: `git-commit` | **Package**: `langchain-anthropic>=0.3.0`
- **Thay đổi**: Tích hợp Claude 3.5 Sonnet / Claude 3 Opus; hỗ trợ streaming token, reasoning tokens và function calling.

### `providers.openai`
#### [0.1.0] — 2026-09-23
- **Artifact**: `git-commit` | **Package**: `langchain-openai>=0.2.0`
- **Thay đổi**: Tích hợp GPT-4o / GPT-4o-mini; hỗ trợ function calling, JSON mode và streaming.

### `providers.ollama`
#### [0.1.0] — 2026-09-23
- **Artifact**: `git-commit` | **Package**: `langchain-ollama>=0.2.0`
- **Thay đổi**: Hỗ trợ chạy offline local models (Llama 3, DeepSeek-R1, Mistral, Qwen) không cần Internet.

### `providers.mistral`
#### [0.1.0] — 2026-09-23
- **Artifact**: `git-commit` | **Package**: `langchain-mistralai>=0.2.0`
- **Thay đổi**: Tích hợp Mistral Large 2 và Codestral cho tác vụ phân tích mã nguồn.

### `providers.deepseek`
#### [0.1.0] — 2026-09-23
- **Artifact**: `git-commit` | **Package**: `langchain-openai` (OpenAI-compatible)
- **Thay đổi**: Hỗ trợ DeepSeek-V3 và DeepSeek-R1 với luồng reasoning/thinking chuyên sâu.

### `providers.nvidia_nim`
#### [0.1.0] — 2026-09-23
- **Artifact**: `git-commit` | **Package**: `langchain-nvidia-ai-endpoints>=0.3.0`
- **Thay đổi**: Tích hợp NVIDIA NIM Microservices cho inference tăng tốc trên GPU.

### `providers.qwen`
#### [0.1.0] — 2026-09-23
- **Artifact**: `git-commit` | **Package**: `langchain-openai` (OpenAI-compatible)
- **Thay đổi**: Tích hợp Qwen 2.5 Coder cho phân tích payload và kịch bản khai thác.

### `providers.opencode`
#### [0.1.0] — 2026-09-23
- **Artifact**: `git-commit` | **Package**: `langchain-openai` (OpenAI-compatible)
- **Thay đổi**: Hỗ trợ endpoint OpenAI-compatible tùy biến của tổ chức.

### `providers.kilo`
#### [0.1.0] — 2026-09-23
- **Artifact**: `git-commit` | **Package**: `langchain-openai` (OpenAI-compatible)
- **Thay đổi**: Hỗ trợ local cluster inference gateway.

---

## 3. System Agents (`agents.*`)

### `agents.orchestrator` (Agent Điều Phối / Ông)
#### [0.1.0] — 2026-09-23
- **Artifact**: `git-commit`
- **Thay đổi**: Tiếp nhận mission tổng, phân tích mục tiêu cấp cao, lập kế hoạch chiến lược và ủy quyền cho các Agent Cha.

### `agents.planner`
#### [0.1.0] — 2026-09-23
- **Artifact**: `git-commit`
- **Thay đổi**: Lập kế hoạch theo các chiến lược CoT (Chain of Thought), ReAct, và ToT (Tree of Thought).

### `agents.reasoner`
#### [0.1.0] — 2026-09-23
- **Artifact**: `git-commit`
- **Thay đổi**: Phân tích suy luận logic chuyên sâu, đối chiếu bề mặt tấn công với cơ sở tri thức.

### `agents.researcher`
#### [0.1.0] — 2026-09-23
- **Artifact**: `git-commit`
- **Thay đổi**: Tra cứu thông tin lỗ hổng CVE, tài liệu API, PoC công khai và công nghệ mục tiêu.

### `agents.analyzer`
#### [0.1.0] — 2026-09-23
- **Artifact**: `git-commit`
- **Thay đổi**: Phân tích kết quả đầu ra thô của các công cụ (Nmap, Nikto, SQLMap) để tìm finding xác thực.

### `agents.reporter`
#### [0.1.0] — 2026-09-23
- **Artifact**: `git-commit`
- **Thay đổi**: Biên soạn báo cáo bảo mật tự động ra các định dạng Markdown, JSON, HTML và PDF.

### `agents.tool_router`
#### [0.1.0] — 2026-09-23
- **Artifact**: `git-commit`
- **Thay đổi**: Điều phối tham số và ủy quyền thực thi công cụ vào Kali Docker sandbox an toàn.

---

## 4. Security Tools & Sandbox (`tools.*`)

### `tools.nmap`
#### [7.95] — 2026-09-23
- **Artifact**: `docker-tag` | **Environment**: Kali Linux Docker Sandbox
- **Thay đổi**: Quét cổng TCP/UDP, phát hiện phiên bản dịch vụ (`-sV`) và hệ điều hành (`-O`).

### `tools.gobuster`
#### [3.6.0] — 2026-09-23
- **Artifact**: `docker-tag` | **Environment**: Kali Linux Docker Sandbox
- **Thay đổi**: Brute-force thư mục web (dir mode), phát hiện file ẩn và vhost.

### `tools.sqlmap`
#### [1.8] — 2026-09-23
- **Artifact**: `docker-tag` | **Environment**: Kali Linux Docker Sandbox
- **Thay đổi**: Tự động phát hiện và kiểm chứng các dạng lỗ hổng SQL Injection.

### `tools.nikto`
#### [2.1.6] — 2026-09-23
- **Artifact**: `docker-tag` | **Environment**: Kali Linux Docker Sandbox
- **Thay đổi**: Quét cấu hình sai trên web server, file mặc định nguy hiểm và header bảo mật.

### `tools.whois`
#### [5.5.23] — 2026-09-23
- **Artifact**: `docker-tag` | **Environment**: Kali Linux Docker Sandbox
- **Thay đổi**: Tra cứu thông tin đăng ký tên miền, dải địa chỉ IP và ASN mục tiêu.

### `tools.curl`
#### [8.9] — 2026-09-23
- **Artifact**: `docker-tag` | **Environment**: Kali Linux Docker Sandbox
- **Thay đổi**: Gửi raw HTTP request tùy biến header, payload và phương thức kiểm thử.

---

## 5. Packages (`packages.*`)

### `packages.weasyprint`
#### [62.3] — 2026-09-23
- **Artifact**: `pypi` | **Package**: `weasyprint>=62.3`
- **Thay đổi**: Engine biên dịch báo cáo đánh giá bảo mật từ HTML/CSS sang file PDF chất lượng cao.

### `packages.asyncpg`
#### [0.29.0] — 2026-09-23
- **Artifact**: `pypi` | **Package**: `asyncpg>=0.29.0`
- **Thay đổi**: Client kết nối bất đồng bộ tùy chọn đến cơ sở dữ liệu PostgreSQL ngoài.

---

## 6. Extensions & Plugins (`extensions.*`)

### `extensions.burp_importer`
#### [0.1.0] — 2026-09-23
- **Artifact**: `zip` | **Source**: `burp_importer.zip`
- **Thay đổi**: Plugin phân tích và chuẩn hóa kết quả quét xuất từ Burp Suite XML vào bộ nhớ hệ thống.

### `extensions.nuclei_templates`
#### [1.0.0] — 2026-09-23
- **Artifact**: `git-tag` (`v1.0.0`)
- **Thay đổi**: Thư viện mẫu quét nhận diện lỗ hổng bảo mật cộng đồng cho deep scanning.
