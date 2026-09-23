# SecurityAgent

A modular, multi-agent system for automated security research and penetration testing.
Built on **LangGraph** and **Deep Agents** with a clean, extensible architecture.

---

## Features

- **Multi-Agent Orchestration** — LangGraph StateGraph with Planner, Reasoner, Analyzer, Reporter agents
- **Provider Abstraction** — Swap between Claude, OpenAI, Ollama, Mistral, DeepSeek, NVIDIA NIM, Qwen, and more
- **Isolated Sandbox** — All tool execution inside Docker (Kali Linux), never on the host
- **Real-time Monitoring** — WebSocket/SSE streaming of agent events, tool output, and execution status
- **Independent Versioning** — Tools, agents, providers, extensions version independently
- **Rich Reports** — Markdown, JSON, HTML, PDF export
- **Web UI + REST API** — Self-hosted, port > 8000

---

## Quick Start

### Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) or pip
- Docker

### Install

```bash
# Clone
git clone git@github.com:snn206/SecurityAgent.git
cd SecurityAgent

# Copy environment config
cp .env.example .env
# Edit .env — add your API keys

# Install (using uv)
uv pip install -e ".[dev]"

# Or using pip
pip install -e ".[dev]"
```

### Build Sandbox

```bash
make sandbox-build
```

### Run

```bash
# Development mode (auto-reload)
make dev

# Production (Docker stack)
make docker-up
```

Open `http://localhost:8080` in your browser.

---

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full system diagram and layer descriptions.

```
UI / API  →  OrchestratorAgent  →  Planner  →  ToolRouter
          →  Sandbox (Docker/Kali)  →  stdout/stderr
          →  AnalyzerAgent  →  ReporterAgent  →  Report
```

---

## Configuration

All configuration lives in `config/`:

| File | Purpose |
|------|---------|
| `config/settings.yaml` | Global settings (ports, paths, logging) |
| `config/providers.yaml` | Provider configs (API keys via env vars) |
| `config/agents.yaml` | Agent definitions and roles |
| `config/planning.yaml` | Planning role → provider/model mapping |
| `config/tools.yaml` | Tool catalog with Docker commands |
| `config/sandbox.yaml` | Docker sandbox settings |

---

## Versioning

Components version independently. See `registry/versions.yaml`.

```bash
make versions                                    # list all component versions
make update                                      # update all to latest
make update-component COMPONENT=tools.nmap       # update single tool
make rollback COMPONENT=providers.anthropic VERSION=1.2.0
```

---

## API

REST API at `http://localhost:8080/api/v1/`

| Method | Endpoint | Description |
|--------|---------|-------------|
| POST | `/tasks` | Submit a new task |
| GET | `/tasks/{id}` | Get task status |
| GET | `/executions/{id}` | Get full execution trace |
| GET | `/reports/{id}` | Download report |
| GET | `/providers` | List available providers |
| GET | `/tools` | List available tools |
| GET | `/health` | Health check |

**WebSocket**: `ws://localhost:8080/ws/{execution_id}` — Real-time events

**SSE**: `http://localhost:8080/stream/{execution_id}` — Server-sent events

---

## Development

```bash
make test           # run all tests
make lint           # ruff check
make typecheck      # mypy
make format         # ruff format
make coverage       # test coverage report
```

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

---

## License

MIT
