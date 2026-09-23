# Sandbox Guide

## Overview

All tool execution is isolated inside a **Docker Kali Linux container**. No commands run on the host.

## Setup

```bash
# Build sandbox image
make sandbox-build
# or
docker build -f docker/Dockerfile.sandbox -t security-agent-sandbox:latest docker/
```

## Configuration

Edit `config/sandbox.yaml`:

```yaml
sandbox:
  image: "security-agent-sandbox:latest"
  network_mode: "bridge"   # or "none" for full isolation
  resources:
    cpu_count: 2
    mem_limit: "2g"
  default_timeout: 300
```

## Tool Sync

To install/update tools in the sandbox:

```bash
python scripts/update.py update all   # updates all tools
python scripts/update.py update tools.nmap
```

Or use `ToolSync` programmatically:

```python
from security_agent.sandbox.sync import ToolSync
sync = ToolSync()
await sync.sync_all()
```

## Flow

```
Agent → CommandExecutor → docker run security-agent-sandbox
                             → bash -c "<command>"
                             → stdout / stderr / exit_code
                         ← ExecutionResult
```
