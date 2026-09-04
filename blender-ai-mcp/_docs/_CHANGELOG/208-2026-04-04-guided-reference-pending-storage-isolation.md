# 208. Guided reference pending storage isolation

Date: 2026-04-04

## Summary

Hardened blocked guided-session reference bookkeeping so staged pending
references no longer alias the active goal-scoped reference set or delete files
behind still-active records.

## What Changed

- updated `reference_images(...)` blocked-session handling to:
  - keep staged `attach` writes scoped to `pending_reference_images`
  - present one combined visible list across active and pending refs
  - deduplicate the visible list by `reference_id`
  - let blocked-session `remove` update the correct active/pending store(s)
  - let blocked-session `clear` safely clear both stores when both are visible
- added best-effort file cleanup deduplication so the same staged/active path is
  not unlinked multiple times during recovery flows
- added focused regression coverage for:
  - same-goal `ready` -> `needs_input` -> staged attach
  - removing an active ref while staged refs still exist
  - clearing blocked-session refs without leaving stale active `stored_path`
    metadata behind
- updated README, MCP/Vision docs, prompt docs, tool summary, and task-board
  lineage notes to describe the hardened active-vs-pending separation

## Why

The earlier pending-adoption wave made blocked guided sessions usable, but a
later regression review found that staged refs could be bootstrapped from the
active set. That let blocked-session `remove` / `clear` delete temp files for
active refs without removing the active records, which later compare/iterate
flows still trusted.

## Validation

- `poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
