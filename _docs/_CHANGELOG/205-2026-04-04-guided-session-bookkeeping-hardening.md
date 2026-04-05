# 205. Guided session bookkeeping hardening

Date: 2026-04-04

## Summary

Hardened guided MCP session bookkeeping so router execution diagnostics no
longer rewrite the full session capability snapshot from sync routed tool
paths.

## What Changed

- narrowed `record_router_execution_outcome(...)` to persist only:
  - `last_router_disposition`
  - `last_router_error`
- removed the sync full-session rewrite from router execution bookkeeping so
  unrelated guided state such as:
  - active `goal`
  - adopted `reference_images`
  - pending guided handoff/session metadata
  is no longer at risk of being clobbered by diagnostics writes
- added regression coverage for the async-style FastMCP `Context` case where
  sync bookkeeping runs while a loop is active and must preserve existing
  goal-scoped state
- re-ran the guided session/reference unit packs after the change

## Why

The guided/reference surface depends on session-scoped FastMCP state surviving
normal routed modeling/tool calls. Diagnostics bookkeeping only needs the last
router disposition and error, so rewriting the whole session snapshot from that
path created unnecessary risk around guided goal/reference continuity.
