# 179. RPC poll budget and disabled vision conflict guard

Date: 2026-04-01

## Summary

Closed two runtime edge cases: addon-job polling/collection now respects the
remaining MCP task budget per call, and disabled vision runtime config no
longer fails fast on mixed generic external provider env.

## What Changed

- `run_rpc_background_job(...)` now binds each `rpc.get_job` and
  `rpc.collect_job` call to the remaining `MCP_TASK_TIMEOUT_SECONDS` budget
- `RpcClient.send_request(...)` now supports a per-call client/socket timeout
  override instead of always waiting up to global `RPC_TIMEOUT_SECONDS`
- disabled vision runtime no longer raises a generic-provider model conflict
  when both `VISION_OPENROUTER_MODEL` and `VISION_GEMINI_MODEL` are populated
- added regression coverage for:
  - remaining-budget propagation on addon-job poll/collect calls
  - disabled vision runtime with conflicting generic external provider env

## Why

Without the per-call bound, one long poll or collect RPC could outlive the
configured task deadline. Without the disabled-runtime guard, unrelated env
noise could still break bootstrap even when vision was explicitly turned off.
