# TASK-141-01-01: `call_tool(...)` Wrapper Aliases and Cleanup-Flag Compatibility

**Parent:** [TASK-141-01](./TASK-141-01_Guided_Call_Path_Compatibility_And_Public_Contract_Ergonomics.md)
**Status:** ✅ Done
**Priority:** 🔴 High

**Completion Summary:** The canonical `call_tool(name=..., arguments=...)`
wrapper and guided `scene_clean_scene(...)` cleanup flag story now match on the
active surface. Legacy wrapper aliases and split cleanup flags remain narrow
compatibility paths, and both direct/proxied failures now return deterministic
guided guidance.

## Objective

Define one deterministic compatibility policy for guided `call_tool(...)`
wrapper drift and `scene_clean_scene(...)` cleanup flags, then prove that the
same policy survives the actual active shaped surface and transport path.

## Business Problem

The repo already contains compatibility logic for wrapper aliases and cleanup
flags, but the real guided squirrel run still found a mismatch between the
documented contract and what surfaced through the live `call_tool(...)` path.

This leaf therefore owns two things at once:

- one explicit compatibility envelope for wrapper aliases and cleanup flags
- proof that the envelope holds on the real active guided surface instead of
  stopping at helper-level unit coverage

## Repository Touchpoints

- `server/adapters/mcp/discovery/search_surface.py`
- `server/adapters/mcp/factory.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `_docs/_PROMPTS/README.md`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- the canonical public form stays `call_tool(name=..., arguments=...)`
- the runtime behavior for wrapper drift is explicit and regression-tested:
  - accepted compatibility aliases, if any, are narrow and deterministic
  - rejected shapes fail with actionable guidance, not vague schema noise
- split cleanup flags remain compatibility-only and cannot silently override or
  blur `keep_lights_and_cameras`
- proxied validation/runtime failures still preserve the same failure
  semantics as direct tool execution on the active guided surface
- E2E surface regressions cover canonical, compatibility, and rejected shapes
  through real `call_tool(...)` execution instead of only direct helper calls

## Leaf Work Items

- decide whether wrapper alias compatibility is supported or rejected with
  guided contract messaging
- keep `scene_clean_scene(...)` split-flag handling compatible with the same
  contract policy
- close any parity gap between helper-level canonicalization and the real
  active guided surface path
- add focused unit plus E2E regression coverage for canonical, compatibility,
  and ambiguous failure shapes

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped

## Status / Board Update

- keep board tracking on `TASK-141`
- reflect the final wrapper-policy decision and active-surface parity result in
  the parent task summary when this leaf closes

## Validation

- `poetry run pytest tests/unit/adapters/mcp/test_search_surface.py -q`
- `poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py -q`
