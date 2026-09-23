# Versioning Guide

## Overview

SecurityAgent uses **independent semantic versioning** for each component.
No component version is locked to another.

## Version Format

`MAJOR.MINOR.PATCH` — follows [SemVer 2.0](https://semver.org/).

- **MAJOR**: Breaking changes
- **MINOR**: New features, backward-compatible
- **PATCH**: Bug fixes

## Component Types & Artifacts

| Type | Artifact | Registry Key |
|------|---------|-------------|
| Core | git-tag | `core` |
| Providers | git-commit | `providers.<name>` |
| Agents | git-commit | `agents.<name>` |
| Tools | docker-tag | `tools.<name>` |
| Packages | pypi / zip | `packages.<name>` |
| Extensions | zip / git-tag | `extensions.<name>` |

## Commands

```bash
# View all versions
python scripts/update.py list

# Update all components to latest
python scripts/update.py update all
# or: make update

# Update a single component
python scripts/update.py update tools.nmap
python scripts/update.py update providers.anthropic

# Rollback a component
python scripts/update.py rollback providers.anthropic 1.2.0

# View component details
python scripts/update.py info tools.nmap
```

## Registry File

All versions are in `registry/versions.yaml`. Each component entry follows `registry/schemas/component.schema.json`.

## Changelog

- Global: `CHANGELOG.md`
- Per-component: `registry/changelog/<type>/<name>.md`
