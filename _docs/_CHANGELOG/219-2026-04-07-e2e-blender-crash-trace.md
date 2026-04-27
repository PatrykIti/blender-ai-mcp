# 219. E2E Blender crash trace and runtime logs

Date: 2026-04-07

## Summary

Added always-on crash-trace diagnostics for unstable Blender E2E runs: the
addon now writes a durable per-RPC trace file, and the automated E2E runner
now always captures Blender stdout/stderr into a dedicated runtime log.

## What Changed

- extended `blender_addon/infrastructure/rpc_server.py` with a durable
  newline-delimited JSON trace file for:
  - received RPC commands
  - handler start/completion/error
  - timeout events
  - background job lifecycle events
- default addon trace directory is now:
  `/tmp/blender-ai-mcp/`
- added `BLENDER_AI_MCP_TRACE_DIR` override for the addon-side trace location
- updated `scripts/run_e2e_tests.py` so each automated Blender launch always
  writes stdout/stderr to:
  - `tests/e2e/blender_runtime_YYYYMMDD_HHMMSS.log`
- updated the saved E2E pytest session log to embed:
  - the Blender runtime log path
  - a tail of the Blender runtime log
- added unit coverage for both the addon-side trace file and the runner-side
  runtime log behavior
- documented the new artifacts in addon/test docs so operators know where to
  look after a sudden Blender disappearance

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/rpc/test_rpc_server_edge_cases.py tests/unit/scripts/test_script_tooling.py -q`
- result: `23 passed`

## Why

Intermittent Blender exits during E2E runs are hard to diagnose when the only
artifact is a skipped test tail. These two logs are intentionally always-on so
the next failure leaves a durable trail of:

- the last visible Blender runtime output
- the last RPC command that actually entered addon execution
