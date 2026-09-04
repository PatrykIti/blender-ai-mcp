# 249. Guided create failure and new-goal registry reset

Date: 2026-04-22

## Summary

Fixed three guided-session flow issues:

- failed guided create calls no longer auto-register semantic roles
- starting a different guided goal now resets prior guided part registration
- empty-scene bootstrap now distinguishes Blender's stock startup scene from a
  real lone object still named like a default primitive

## What Changed

- in `server/adapters/mcp/areas/modeling.py`:
  - guided-role convenience registration after create now requires an actual
    successful created-object result instead of falling back to the requested
    name on failure strings
- in `server/adapters/mcp/session_capabilities.py`:
  - `update_session_from_router_goal(...)` and async parity now clear
    `guided_part_registry` for a different goal instead of seeding the new flow
    with prior completed roles
- in `server/adapters/mcp/areas/router.py`:
  - refined `_scene_has_meaningful_guided_objects()` so Blender's stock
    startup scene still uses empty-scene bootstrap while a real lone object
    named `Cube` / `Sphere` / etc. counts as existing geometry
- updated public docs in:
  - `README.md`
  - `_docs/_MCP_SERVER/README.md`
  so guided bootstrap and registration behavior matches the shipped runtime

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit -q`
  - result on this machine: `3054 passed`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  - result on this machine: passed
