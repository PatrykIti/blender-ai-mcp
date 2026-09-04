# 233. Generic guided governor hardening

Date: 2026-04-10

## Summary

Completed TASK-130 by tightening the generic guided governor around three
practical failure modes seen in real long-running sessions:

- active spatial-gate tools now require explicit scope more consistently
- staged compare/iterate no longer escalates too early into
  `inspect_validate` when the current guided role/workset slice is still
  incomplete
- `search_tools(...)` now behaves better for exact tool-name lookups and uses a
  more compact result shape

## What Changed

- tightened active spatial-gate scope discipline in:
  - `server/adapters/mcp/areas/scene.py`
  so `scene_scope_graph(...)`, `scene_relation_graph(...)`, and
  `scene_view_diagnostics(...)` now all require explicit
  `target_object` / `target_objects` / `collection_name` when the guided
  runtime is actively waiting on spatial-context progress
- refined staged iteration governor behavior in:
  - `server/adapters/mcp/areas/reference.py`
  so high-priority truth findings can still remain truth-first, but the server
  now holds the loop in `continue_build` when the current guided build stage
  still has missing role/workset obligations
- hardened guided discovery in:
  - `server/adapters/mcp/discovery/search_surface.py`
  by:
  - returning exact tool-name matches immediately when visible
  - serializing search results into a smaller, more focused payload
  instead of dumping full list-tools-style tool definitions for common lookup
  queries
- added/updated regression coverage in:
  - `tests/unit/adapters/mcp/test_scene_guided_scope_requirements.py`
  - `tests/unit/adapters/mcp/test_reference_images.py`
  - `tests/unit/adapters/mcp/test_search_surface.py`
  plus the broader guided-flow / docs / transport parity matrix
- updated task planning/history for the repurposed TASK-130 umbrella and moved
  it to Done once the runtime, transport, docs, and changelog pieces landed

## Why

The guided runtime already had the right core pieces from TASK-149 through
TASK-154, but the model could still drift in practice by:

- calling spatial helpers with implicit/no scope
- switching into inspect/validate too early while the current build slice was
  still incomplete
- drowning in overly large discovery payloads for simple exact-name lookups

These changes do not add a second planner.
They tighten the existing server-owned governor so the correct next move is
more explicit and easier for the model to follow across `creature`,
`building`, and fallback `generic` sessions.

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_scene_guided_scope_requirements.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_search_surface.py -q -k 'hold_build or exact_match_returns_compact or requires_explicit_scope'`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_router_elicitation.py tests/unit/adapters/mcp/test_scene_guided_scope_requirements.py -q -k 'not slow'`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py tests/e2e/integration/test_guided_streamable_spatial_support.py tests/e2e/integration/test_guided_inspect_validate_handoff.py -q`
  - result on this machine: `4 passed, 2 skipped`
