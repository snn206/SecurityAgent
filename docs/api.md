# API Reference

Base URL: `http://localhost:8080/api/v1`

## Endpoints

### Tasks

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/tasks` | Submit a new task |
| `GET` | `/tasks` | List recent tasks |
| `GET` | `/tasks/{task_id}` | Get task status |

#### POST /tasks

```json
{
  "user_request": "Scan 192.168.1.100 for open ports",
  "scope": "192.168.1.100",
  "provider": "anthropic",
  "model": "claude-opus-4-5"
}
```

### Executions

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/executions/{id}` | Full execution record |
| `GET` | `/executions/{id}/events` | Event trace |

### Reports

| Method | Path | Query | Description |
|--------|------|-------|-------------|
| `GET` | `/reports/{id}` | `format=json\|markdown\|html` | Download report |

### Providers & Tools

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/providers` | List loaded providers |
| `GET` | `/tools` | List available tools |
| `GET` | `/health` | Health check |

## WebSocket

`ws://localhost:8080/ws/{execution_id}`

Real-time event stream. Send `"ping"` to keep alive.

## SSE

`GET http://localhost:8080/stream/{execution_id}`

Server-sent events stream — alternative to WebSocket.
