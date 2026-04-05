# 212. Stage compare error response hardening

Date: 2026-04-05

## Summary

Hardened the staged reference-compare error path so invalid target-scope input
returns a structured MCP error payload instead of failing again while building
the response.

## What Changed

- `_stage_compare_response(...)` no longer re-runs assembled target-scope
  resolution on every response path
- `reference_compare_stage_checkpoint(...)` now passes the already-resolved
  `assembled_target_scope` on success paths and leaves it `null` on the
  collection-resolution error path
- invalid `collection_name` input now returns the intended structured
  `error=str(exc)` payload instead of risking an uncaught tool failure from a
  second scope-resolution step
- added focused regression coverage for the invalid-collection structured-error
  path
- updated MCP docs to note that invalid stage-compare target scope returns a
  structured error payload

## Why

The stage-compare path already had an explicit `except RuntimeError` branch for
bad collection scope. Re-resolving that same scope inside the response builder
undermined the contract by letting the error path fail a second time.

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
