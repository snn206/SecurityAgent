# SecurityAgent — Architecture

## Overview

SecurityAgent is a modular, multi-agent system for automated security research and penetration testing. It orchestrates LangGraph-based agents through a clean layered architecture — from user request to sandboxed tool execution and report generation.

```
┌────────────────────────────────────────────────────────────────┐
│                          Interface Layer                       │
│              Web UI  /  REST API  /  WebSocket  /  SSE         │
└────────────────────────────────────┬───────────────────────────┘
                                     │
┌────────────────────────────────────▼───────────────────────────┐
│                        Orchestration Layer                     │
│          OrchestratorAgent  (LangGraph StateGraph)             │
│   ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│   │   Planner   │  │   Reasoner   │  │  ResearchAgent     │   │
│   └─────────────┘  └──────────────┘  └────────────────────┘   │
│   ┌──────────────────────┐  ┌────────────────────────────────┐ │
│   │    AnalyzerAgent     │  │       ReporterAgent            │ │
│   └──────────────────────┘  └────────────────────────────────┘ │
└────────────────────────────────────┬───────────────────────────┘
                                     │
┌────────────────────────────────────▼───────────────────────────┐
│                      Provider Abstraction Layer                │
│   Claude │ OpenAI │ Ollama │ Mistral │ DeepSeek │ NVIDIA NIM   │
│                   Qwen │ OpenCode │ Kilo │ …                   │
└────────────────────────────────────┬───────────────────────────┘
                                     │
┌────────────────────────────────────▼───────────────────────────┐
│                       Tool Router Layer                        │
│              ToolRegistry → ToolRouter → Tool                  │
└────────────────────────────────────┬───────────────────────────┘
                                     │
┌────────────────────────────────────▼───────────────────────────┐
│                         Sandbox Layer                          │
│          Docker (Kali Linux) — isolated execution              │
│   SandboxManager → CommandExecutor → Tool/Command             │
│                  stdout / stderr / exit code                   │
└────────────────────────────────────┬───────────────────────────┘
                                     │
┌────────────────────────────────────▼───────────────────────────┐
│                      Execution & History                       │
│         ExecutionTracker → HistoryStore (SQLite/Postgres)      │
└────────────────────────────────────┬───────────────────────────┘
                                     │
┌────────────────────────────────────▼───────────────────────────┐
│                         Report Layer                           │
│        ReportBuilder → Markdown / JSON / HTML / PDF           │
└────────────────────────────────────────────────────────────────┘
```

---

## Layers

### 1. Interface Layer
- **Web UI** — Single-page app served by FastAPI, real-time updates via WebSocket/SSE.
- **REST API** — FastAPI, port `8080`. Task submission, status polling, report download.
- **WebSocket** — `/ws` — Streams execution events, agent activity, command output.
- **SSE** — `/stream/{execution_id}` — Alternative to WebSocket for read-only consumers.

### 2. Orchestration Layer (LangGraph + Deep Agents)
- `OrchestratorAgent` — Root LangGraph `StateGraph`. Routes tasks to sub-agents.
- `PlannerAgent` — Produces a structured `Plan` (steps, tool choices, agent assignments).
- `ReasonerAgent` — Evaluates intermediate results, decides next action.
- `ResearchAgent` — OSINT, passive recon, web search.
- `AnalyzerAgent` — Interprets tool output, extracts findings.
- `ReporterAgent` — Aggregates all findings into a final report.
- `ToolRouterAgent` — Selects and invokes the right tool for each step.

### 3. Provider Abstraction Layer
All providers implement `AbstractProvider`. Config lives in `config/providers.yaml`.

| Provider     | Auth       | Tool Calling | Streaming | Reasoning |
|-------------|-----------|-------------|----------|----------|
| Claude       | API Key    | ✓           | ✓        | ✓ (extended thinking) |
| OpenAI       | API Key    | ✓           | ✓        | ✓ (o-series) |
| Ollama       | None       | ✓ (model-dependent) | ✓ | — |
| Mistral      | API Key    | ✓           | ✓        | — |
| DeepSeek     | API Key    | ✓           | ✓        | ✓ |
| NVIDIA NIM   | API Key    | ✓           | ✓        | — |
| Qwen         | API Key    | ✓           | ✓        | ✓ |
| OpenCode     | API Key    | ✓           | ✓        | — |
| Kilo         | API Key    | ✓           | ✓        | — |

### 4. Planning / Thinking Layer
Separate planning strategies. Each planning role can use a different provider/model:

| Role        | Default Provider | Strategy |
|-------------|-----------------|---------|
| Planning    | configurable    | Chain-of-Thought / ReAct |
| Reasoning   | configurable    | Tree-of-Thought |
| Research    | configurable    | ReAct |
| Execution   | configurable    | Direct |
| Tool Calling| configurable    | Direct |

### 5. Tool Layer
Tools are registered in `config/tools.yaml` and loaded via `ToolRegistry`. Every tool is a Docker command or API call — **no commands run on the host**.

Built-in tools: `nmap`, `gobuster`, `sqlmap`, `nikto`, `whois`, `curl`, `shell`.

### 6. Sandbox Layer
- Docker container running **Kali Linux**.
- `SandboxManager` — lifecycle: create, start, stop, remove.
- `CommandExecutor` — sends commands to container, captures stdout/stderr/exit code.
- `ToolSync` — auto-installs/updates tools inside the container.

### 7. Execution & History
- Every task gets a unique `execution_id`.
- `ExecutionTracker` emits `ExecutionEvent` objects in real time.
- `HistoryStore` persists all events to SQLite (default) or PostgreSQL.

### 8. Report Layer
- `ReportBuilder` aggregates execution trace into a structured report.
- Exporters: Markdown, JSON, HTML, PDF.
- Jinja2 templates in `src/security_agent/reports/templates/`.

---

## Data Flow

```
User Request
  → API (POST /tasks)
    → OrchestratorAgent (LangGraph)
      → PlannerAgent → Plan (YAML/JSON)
        → For each step:
            → ToolRouterAgent → Tool selection
              → SandboxManager → Docker container
                → CommandExecutor → stdout/stderr/exit_code
                  → ExecutionTracker (event stream → WebSocket/SSE)
      → AnalyzerAgent → Findings
      → ReporterAgent → Report
  → API (GET /reports/{execution_id})
    → Download Markdown/HTML/PDF
```

---

## Versioning Model

Each component has an independent semantic version (`MAJOR.MINOR.PATCH`):

| Component Type | Version Location | Artifact |
|----------------|-----------------|---------|
| Tools | `registry/versions.yaml` → `tools.<name>` | Git tag / Docker layer |
| Packages | `registry/versions.yaml` → `packages.<name>` | PyPI / local wheel |
| Extensions | `extensions/<name>/manifest.yaml` | .zip / Git tag |
| Agents | `registry/versions.yaml` → `agents.<name>` | Git commit |
| Providers | `registry/versions.yaml` → `providers.<name>` | Git commit |
| System Core | `pyproject.toml` | Git tag / PyPI |

Update/rollback commands:
```bash
python scripts/update.py update all          # update everything to latest
python scripts/update.py update tools.nmap   # update single tool
python scripts/update.py rollback providers.anthropic 1.2.0
```

---

## Directory Structure

```
security-agent/
├── src/security_agent/       # Core Python package
│   ├── core/                 # Base classes, events, state, exceptions
│   ├── providers/            # Provider abstraction + implementations
│   ├── planning/             # Planner, Reasoner, Researcher, Strategies
│   ├── agents/               # All agents + registry
│   ├── graph/                # LangGraph builder, nodes, edges
│   ├── tools/                # Tool registry + built-in tools
│   ├── sandbox/              # Docker sandbox manager + executor
│   ├── execution/            # Execution tracking + history
│   ├── reports/              # Report builder + exporters
│   ├── api/                  # FastAPI app + routers + WS/SSE
│   └── ui/                   # Static Web UI
├── config/                   # YAML configs (providers, agents, tools, sandbox)
├── registry/                 # Version registry + changelogs + schemas
├── scripts/                  # update.py, version.py
├── docker/                   # Dockerfiles + compose + Kali setup
├── extensions/               # Extension system
├── packages/                 # Custom installable packages
├── tests/                    # Unit + integration tests
├── docs/                     # Documentation
├── pyproject.toml            # Package metadata + dependencies
├── Makefile                  # Developer commands
└── .env.example              # Environment variable template
```
