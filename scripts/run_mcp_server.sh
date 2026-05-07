#!/usr/bin/env bash

set -euo pipefail

exec poetry run python scripts/run_mcp_server.py "$@"
