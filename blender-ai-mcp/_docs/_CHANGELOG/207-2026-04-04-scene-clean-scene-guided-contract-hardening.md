# 207. scene_clean_scene guided contract hardening

Date: 2026-04-04

## Summary

Closed `TASK-127` by hardening the guided utility/public contract for
`scene_clean_scene(...)` so legacy split cleanup flags no longer break normal
`llm-guided` discovery flows.

## What Changed

- kept `keep_lights_and_cameras` as the one canonical public cleanup flag
  for `scene_clean_scene(...)`
- added guided `call_tool(...)` compatibility for the older split cleanup form:
  - `keep_lights`
  - `keep_cameras`
- legacy split cleanup flags are now accepted only when both values are
  provided and agree, so they collapse cleanly to the canonical combined flag
- mixed split values now fail with one deterministic contract error that points
  the caller back to `keep_lights_and_cameras`
- aligned user-facing docs and prompts so they continue to teach the canonical
  cleanup shape instead of the legacy split form
- updated the tool summary and task board state to reflect the closed follow-on

## Validation

- `poetry run pytest tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
