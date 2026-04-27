# 222. Guided build cleanup recovery hatch

Date: 2026-04-07

## Summary

Completed TASK-147 by exposing `scene_clean_scene(...)` on the guided build
surface as a bounded recovery hatch, while keeping cleanup-before-goal as the
preferred operating model in prompt and MCP docs.

## What Changed

- added `scene_clean_scene(...)` to the guided build surface visibility rules
  for:
  - generic build phase
  - guided manual build supporting tools
  - low-poly creature blockout handoff supporting tools
- updated prompt and MCP docs so the product rule is explicit:
  - cleanup before `router_set_goal(...)` is preferred
  - build-phase cleanup is still allowed when stale scene state is discovered
    later
- updated guided benchmark/search/visibility tests to reflect the new build
  recovery hatch
- added transport-backed integration coverage so `scene_clean_scene(...)`
  remains discoverable/callable after manual/no-match guided handoff
- recorded the repair as `TASK-147` in task history/board state

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_guided_surface_benchmarks.py tests/unit/adapters/mcp/test_public_surface_docs.py tests/e2e/integration/test_guided_surface_contract_parity.py -q`
- result: `58 passed`

## Why

Real guided build sessions can discover stale scene state only after entering
`guided_manual_build`. At that point, rejecting `scene_clean_scene(...)` as
"tool not available" creates unnecessary drift and confusion even though the
correct recovery action is obvious. This repair keeps the guided surface small
while acknowledging that cleanup is still a legitimate build-phase recovery
hatch.
