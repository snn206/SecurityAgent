#!/bin/bash
# SecurityAgent Kali Sandbox Entrypoint
set -e

# Ensure /artifacts and /workspace are writable
mkdir -p /artifacts /workspace

exec "$@"
