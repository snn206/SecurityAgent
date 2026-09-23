# Extensions

Extensions add capabilities to SecurityAgent without modifying the core.

## Structure

Each extension is a directory with:

```
extensions/
  my_extension/
    manifest.yaml    # Required: metadata, version, hooks
    extension.py     # Required: extension implementation
    requirements.txt # Optional: extra Python deps
    README.md        # Optional: documentation
```

## manifest.yaml Schema

```yaml
id: "my_extension"
name: "My Extension"
version: "1.0.0"
description: "What this extension does"
author: "Your Name"
hooks:
  - "on_task_start"
  - "on_tool_selected"
  - "on_report_generated"
dependencies: []
```

## Hooks Available

| Hook | When Called |
|------|------------|
| `on_task_start` | Before a task begins execution |
| `on_plan_created` | After the planner produces a plan |
| `on_tool_selected` | Before a tool is executed |
| `on_sandbox_result` | After sandbox returns output |
| `on_finding` | When a finding is recorded |
| `on_report_generated` | After report is built |

## Versioning

Extensions version independently via `manifest.yaml`. Register in `registry/versions.yaml`:

```yaml
extensions:
  my_extension:
    version: "1.0.0"
    artifact: "zip"
    changelog: "registry/changelog/extensions/my_extension.md"
```

## Example

See `extensions/example_extension/` for a reference implementation.
