# 226. Addon RPC watchdog and E2E RPC startup retry

Date: 2026-04-08

## Summary

Hardened the Blender addon RPC lifecycle and the E2E bootstrap path so the
repo is less sensitive to transient addon/RPC startup timing.

## What Changed

- added a lightweight addon-side RPC listener watchdog in
  `blender_addon/infrastructure/rpc_server.py`
- started/stopped that watchdog from addon `register()` / `unregister()`
- added retry-based E2E RPC availability probing with a real `ping` in
  `tests/e2e/conftest.py`
- documented:
  - addon RPC listener self-healing
  - E2E RPC startup retry behavior
  - the new tuning env vars

## New Env Vars

- `BLENDER_AI_MCP_RPC_WATCHDOG_INTERVAL_SECONDS`
  - default: `5.0`
- `E2E_RPC_STARTUP_WAIT_SECONDS`
  - default: `8.0`
- `E2E_RPC_RETRY_INTERVAL_SECONDS`
  - default: `0.5`

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/rpc/test_rpc_client.py tests/unit/adapters/rpc/test_rpc_server_edge_cases.py tests/unit/adapters/rpc/test_timeout_coordination.py -q`
- `poetry run mypy blender_addon/infrastructure/rpc_server.py blender_addon/__init__.py tests/e2e/conftest.py tests/unit/adapters/rpc/test_rpc_server_edge_cases.py`

## Why

Two separate failure modes were showing up in practice:

- the addon RPC listener could require a manual Blender/addon restart after a
  bad lifecycle state
- `pytest tests/e2e` could skip most Blender-backed suites if RPC was not
  reachable at the exact moment pytest first checked availability

This change adds bounded self-healing where it is safe and reduces false
startup-related skips without pretending that a dead Blender session can be
magically recovered from every failure mode.
