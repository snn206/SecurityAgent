# Changelog

All notable changes to SecurityAgent are documented here.
Each component maintains its own changelog under `registry/changelog/`.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Initial project scaffold

---

## [0.1.0] — 2026-09-23

### Added
- Project scaffold: modular directory structure
- Provider Abstraction Layer (Claude, OpenAI, Ollama, Mistral, DeepSeek, NVIDIA NIM, Qwen, OpenCode, Kilo)
- LangGraph-based Multi-Agent orchestration (OrchestratorAgent, PlannerAgent, AnalyzerAgent, ReporterAgent)
- Planning/Reasoning/Thinking layer with configurable strategies (CoT, ReAct, ToT)
- Docker Kali Linux sandbox for isolated tool execution
- Tool registry with built-in tools: nmap, gobuster, sqlmap, nikto, whois, curl, shell
- FastAPI REST API (port 8080) with WebSocket + SSE streaming
- Web UI (real-time execution monitoring)
- Execution history with unique `execution_id`
- Report generation: Markdown, JSON, HTML, PDF
- Version registry (`registry/versions.yaml`) with independent component versioning
- `scripts/update.py` — update/rollback individual components or all at once
- Config layer: YAML configs for providers, agents, planning, tools, sandbox
- Extension system with manifest-based versioning
- CI/CD: GitHub Actions (ci.yml, release.yml)
- Full documentation: ARCHITECTURE.md, docs/

[Unreleased]: https://github.com/snn206/SecurityAgent/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/snn206/SecurityAgent/releases/tag/v0.1.0
