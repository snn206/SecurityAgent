<!-- graphcode:start -->
# GraphCode — Code Intelligence

This project is indexed by GraphCode as **security-agent** (786 symbols, 1204 relationships). Use GraphCode graph tools to understand code, assess impact, and navigate safely.

> Index stale? Run `node .graphcode/run.cjs analyze --index-only` from the project root — it auto-selects an available runner. No `.graphcode/run.cjs` yet? Install from source (`npm link` in the repo) or `npm i -g graphcode-cli` once published — then `graphcode analyze`.

## Always Do

- **MUST run impact analysis before editing.** Use `impact({name: "symbolName", direction: "upstream"})` (MCP) or `node .graphcode/run.cjs impact --name "symbolName" --direction upstream` (CLI); report callers and risk. Never substitute grep for graph analysis.
- **MUST analyze graph changes before committing.** Use `detect_changes({scope: "all"})` (MCP) or `node .graphcode/run.cjs detect-changes` (CLI). For a regression diff against a branch/commit: `detect_changes({base_ref: "main"})` (MCP; the CLI detects working-tree changes only).
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- **MUST treat `risk: UNKNOWN` as unresolved, not as low.** An empty caller set is not evidence the symbol is unused — it can also mean the callers are not resolvable by the index. Confirm with a text search before treating the symbol as safe to change or delete.
- When exploring unfamiliar code, use `query({search_query: "concept"})` to find the symbols that implement it instead of grepping.
- When you need full context on a specific symbol — callers, callees, references, file location — use `context({name: "symbolName"})`.
- When you need a symbol's role summarized, use `explain({name: "symbolName"})` (deterministic graph explanation; add `use_llm: true` for a natural-language summary).
- When you need the actual code of a symbol, use `read_file({file_path, start_line?, end_line?})` (MCP) — one call instead of an external file tool. Paths are repo-root-relative.
- Before trusting results after git operations (commit, branch switch, pull), check `repo_status({repo})` (MCP) — if it reports the index is stale, run a sync bundle first.
- Use `note_read` / `note_write` (MCP) as a per-repo scratchpad to persist task context across sessions.
- When you need intra-method data flow, use `pdg_query({name: "symbolName"})` — variable reads, callees, and callers/callees edges the parser observed (statement-level v1; control/data-flow across statements is not tracked yet).

## Never Do

- NEVER edit a function, class, or method before MCP/CLI impact analysis.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis, and never read `UNKNOWN` as an all-clear — it means the walk could not answer, which is the one verdict that requires confirming by other means.
- NEVER rename symbols with find-and-replace — use `rename` which understands the call graph.
- NEVER commit before MCP/CLI graph change analysis.

## Resources

| Resource | Use for |
| --- | --- |
| `graphcode://repo/security-agent/context` | Codebase overview, check index freshness |
| `graphcode://repo/security-agent/clusters` | All functional areas |
| `graphcode://repo/security-agent/processes` | All execution flows |
| `graphcode://repo/security-agent/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
| --- | --- |
| Understand architecture / "How does X work?" | `.claude/skills/graphcode-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/graphcode-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/graphcode-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/graphcode-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/graphcode-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/graphcode-cli/SKILL.md` |

<!-- graphcode:end -->

---

# Quy Định Phát Triển & Vận Hành Hệ Thống (SecurityAgent Rules)

Tài liệu này quy định toàn bộ các nguyên tắc kiến trúc, quy trình phân cấp agent, an toàn sandbox, và quản lý phiên bản độc lập mà mọi Agent và lập trình viên **BẮT BUỘC** tuân thủ khi làm việc trên repository này.

---

## 1. Cấu Trúc Hệ Thống & Phân Cấp Agent (10-Agent Hierarchical Brain)

- **Giới hạn số lượng agent**: Toàn hệ thống có tối đa **10 agent** hoạt động đồng thời:
  1. **1 Agent Điều Phối / Ông (`Grandparent Coordinator`)**:
     - Là đầu não trung tâm, tiếp nhận nhiệm vụ từ người dùng, lập kế hoạch chiến lược tổng quát, phân bổ task cho các Agent Cha.
     - Giám sát tiến độ và tổng hợp báo cáo bảo mật cuối cùng.
  2. **3 Agent Cha (`Parent Specialist Leads`)**:
     - Phụ trách 3 domain chuyên biệt:
       - **Recon & Discovery Lead**: Thu thập thông tin, scan cổng, enum subdomain/service.
       - **Web & API Lead**: Kiểm thử các lỗ hổng web (SQLi, XSS, SSRF, IDOR, v.v.).
       - **Network & System Lead**: Khai thác dịch vụ mạng, xác thực cấu hình sai, phân tích hạ tầng.
     - Quản lý tiến trình công việc trong domain của mình, tự đánh giá tính khả thi và ra lệnh sinh Agent Con khi cần chia nhỏ task.
  3. **Tối đa 2 Agent Con (`Child Workers`) cho mỗi Cha**:
     - Agent Cha chỉ được phép sinh tối đa 2 Agent Con trực thuộc để thực thi các tác vụ con song song.
     - Agent Con báo cáo kết quả ngược lên Agent Cha, không được vượt cấp lên Agent Điều Phối.
- **Hàng đợi Task Cha (`Parent Task Queue`)**:
  - Khi số lượng task cần xử lý lớn hơn 3 (vượt quá 3 slot của Agent Cha), hệ thống **BẮT BUỘC** đưa task vào hàng đợi ưu tiên (`PriorityQueue`).
  - Hàng đợi điều phối task theo mức độ ưu tiên (`CRITICAL` > `HIGH` > `MEDIUM` > `LOW`) và đẩy vào Agent Cha ngay khi có slot trống.

---

## 2. Vòng Lặp Đánh Giá JEV & Tiến Hóa Tri Thức (JEV Harness & Evolution)

- **Nguyên lý JEV**: Mọi phát hiện bảo mật và hành động của agent phải trải qua bộ 3 đánh giá độc lập:
  1. **Verifier (Bộ thẩm định)**: Xác thực bằng chứng kỹ thuật (Proof of Concept, raw response, status code). **Tuyệt đối không chấp nhận finding không có bằng chứng thực tế.**
  2. **Evaluator (Bộ đánh giá)**: Đo lường hiệu quả của bước thực thi, tính an toàn và mức độ bám sát mục tiêu nhiệm vụ.
  3. **Judge (Thẩm phán)**: Ra phán quyết cuối cùng (`VERIFIED`, `REJECTED`, `INCONCLUSIVE`).
- **Học hỏi & Rút kinh nghiệm (`Lessons Learned`)**:
  - Sau mỗi task thành công hoặc thất bại, hệ thống tự động chắt lọc bài học kinh nghiệm (`distill`), lưu trữ vào bộ nhớ tiến hóa.
  - Các lần quét sau phải tự động tra cứu bộ nhớ này để tối ưu hóa chiến thuật, tránh lặp lại sai lầm.

---

## 3. Lưu Trữ Kép & Quản Lý Bộ Nhớ Agent (Dual Storage Layer)

- **SQLite Relational Store (`SQLAlchemy + aiosqlite`)**:
  - Chịu trách nhiệm lưu trữ lịch sử thực thi (`executions`), checkpoint trạng thái đồ thị LangGraph (`checkpoints`), và telemetry logs.
- **Embedded NoSQL Document Store (Không cần cài đặt, cú pháp dạng MongoDB)**:
  - Sử dụng TinyDB lưu trữ dạng tài liệu JSON/BSON nhúng sẵn trong ứng dụng.
  - Quản lý các bộ sưu tập: `lessons_learned`, `evolution_rules`, `golden_rules`.
- **Quyền Quản Lý Của Người Dùng (`User Golden Rules`)**:
  - Người dùng có toàn quyền xem, thêm, sửa, xóa, và ghim các "Luật Vàng" (Golden Rules) qua Web UI hoặc API.
  - Luật do người dùng định nghĩa luôn có quyền ưu tiên cao nhất, đè lên các chiến thuật tự sinh của Agent.

---

## 4. Tầng Trừu Tượng Hóa Nhà Cung Cấp LLM (Provider Abstraction)

- Tách rời mã nguồn logic agent khỏi nhà cung cấp mô hình cụ thể.
- Hỗ trợ chuyển đổi nóng (`hot-swap`) giữa:
  - Cloud Providers: `Anthropic` (Claude), `OpenAI`, `DeepSeek`, `Mistral`, `NVIDIA NIM`, `Qwen`.
  - Local / Self-hosted: `Ollama` (Local), `OpenCode`, `Kilo`.
- **Tuyệt đối không hardcode API key** trong mã nguồn. Toàn bộ cấu hình đọc từ `.env` hoặc file cấu hình `config/providers.yaml`.
- Các provider không hỗ trợ function calling gốc phải sử dụng cơ chế fallback prompt injection để đảm bảo trả lời đúng định dạng JSON/Tool call.

---

## 5. Cô Lập Công Cụ & An Toàn Thực Thi (Sandbox Security)

- **Tất cả công cụ bảo mật** (Nmap, Gobuster, SQLMap, Nikto, Whois, cURL, v.v.) **BẮT BUỘC chạy bên trong Docker Container (Kali Linux Sandbox)**.
- **Tuyệt đối không chạy công cụ khai thác trực tiếp trên máy chủ host**.
- Mọi command line string phải được kiểm tra và lọc ký tự độc hại trước khi chuyển vào container.
- Thư mục lưu trữ artifact kết quả quét phải được mount chỉ định và cô lập.

---

## 6. Quy Định Quản Lý Phiên Bản Độc Lập (Independent Versioning Rules)

- **Không khóa version giữa các thành phần**:
  - Các nhóm: `core`, `providers`, `agents`, `tools`, `packages`, `extensions` có vòng đời và phiên bản độc lập.
  - Không ràng buộc phiên bản chéo (ví dụ: nâng cấp provider Anthropic không bắt buộc nâng cấp core).
- **Update / Rollback độc lập**:
  - Cho phép nâng cấp hoặc quay lui từng thành phần riêng lẻ qua CLI (`sa-update`) và Web UI (`VERSIONS` tab).
- **Lệnh cập nhật toàn bộ lên latest**:
  - Cung cấp lệnh `sa-update update all` để cập nhật đồng loạt mọi thành phần lên bản mới nhất.
  - **Không yêu cầu** tính năng update/rollback toàn bộ hệ thống về một phiên bản cố định chung.
- **Quản lý metadata tập trung**:
  - Toàn bộ version, dependency, changelog được định nghĩa tại `registry/versions.yaml`.
- **Đa dạng Artifact**:
  - Core / Extensions: `git-tag`, `git-commit`, `zip`.
  - Providers / Packages: `pypi` (`uv` / `pip`).
  - Tools: `docker-tag` (trong Kali sandbox).
- **Cài đặt trực tiếp từ GitHub**:
  - Hệ thống cho phép cài đặt trực tiếp qua `uv pip install git+ssh://git@github.com/snn206/SecurityAgent.git` hoặc HTTPS.
  - Cho phép ghim version hoặc rollback trực tiếp qua git ref: `...@v0.1.0` hoặc `...@<commit_sha>`.
- **Quy định Changelog**:
  - Ghi chép lịch sử phiên bản phân tách rõ ràng theo từng thành phần, ngắn gọn, súc tích, tuyệt đối không viết lẫn lộn.

---

## 7. Tiêu Chuẩn Chất Lượng Mã Nguồn & CI/CD

- **GraphCode Impact Analysis**: Bắt buộc chạy phân tích đồ thị trước khi chỉnh sửa symbol mã nguồn.
- **Graph Change Analysis**: Bắt buộc kiểm tra thay đổi đồ thị trước khi commit.
- **Linter & Formatter**: Tuân thủ chuẩn `ruff check` và `ruff format`.
- **Type Checking**: Mã nguồn Python phải vượt qua `mypy src/` không có lỗi.
- **Automated Testing**: Mọi commit phải đảm bảo 100% test suite (Unit & Integration tests) đều PASS.

