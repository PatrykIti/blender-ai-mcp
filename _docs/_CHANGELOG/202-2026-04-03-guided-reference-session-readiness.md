# 202. Guided reference session readiness

Date: 2026-04-03

## Summary

Closed `TASK-124` by turning guided goal/reference orchestration into one
explicit session contract instead of a hidden ordering rule.

## What Changed

- added `guided_reference_readiness` to:
  - `router_set_goal(...)`
  - `router_get_status()`
  - `reference_compare_stage_checkpoint(...)`
  - `reference_iterate_stage_checkpoint(...)`
- staged reference compare/iterate now fail fast with machine-readable:
  - `blocking_reason`
  - `next_action`
  - `compare_ready`
  - `iterate_ready`
- pending references now stay staged while the goal is missing or blocked on
  `needs_input`, then adopt automatically when the guided goal session is
  ready
- goal-mismatched pending references remain explicit instead of silently
  retargeting
- prompt/docs assets now describe the natural attach-before-goal flow and tell
  clients to read `guided_reference_readiness` before staged compare/iterate
- added focused unit coverage for:
  - readiness computation
  - pending-reference adoption lifecycle
  - fail-fast staged compare behavior
  - docs regressions for the new readiness contract

## Why

The guided surface already had the right primitives, but the product still
leaked hidden sequencing assumptions such as “set goal first, then attach
refs, then compare.” This change makes that state explicit, keeps natural
request order usable, and gives the model one deterministic next action when
the session is not ready.
