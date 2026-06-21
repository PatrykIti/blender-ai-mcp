# TASK-186-02: Mask-To-Mesh Face Lift And Part Materialization

**Parent:** [TASK-186](./TASK-186_Semantic_Part_Decomposition_And_Registry_Materialization.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Convert bounded decomposition evidence into mesh face groups or separate Blender part objects with explicit provenance and uncertainty.

**Repository Touchpoints:** `blender_addon/application/handlers/`, `server/application/tool_handlers/`, `server/adapters/mcp/contracts/`, `tests/unit/`, `tests/e2e/`

## Implementation Notes

- Define one materialization output for v1:
  - face groups/material slots when geometry should remain one object
  - separate objects only when the operator requests object-level parts or the
    mesh topology supports clean separation
- Preserve source provenance and confidence per part.
- Use deterministic mesh inspection to detect empty, tiny, overlapping, or
  ambiguous groups before registration.

## Runtime / Security Contract Notes

- materialization is mutating and must report mode/selection impact
- no face/group should be deleted implicitly; destructive cleanup requires a
  separate explicit action
- unknown or unsupported payload fields must be rejected in the strict contract

## Tests To Add/Update

- unit tests for contract validation and server-to-RPC payloads
- Blender E2E fixture proving face group or object materialization
- negative E2E for empty/ambiguous part groups

## Docs To Update

- `_docs/_ADDON/README.md`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- decomposition evidence can be materialized into inspectable Blender state
- materialization reports provenance and uncertainty
- invalid/empty materializations fail with meaningful errors

## Validation Commands

- `git diff --check`
- `poetry run python scripts/run_e2e_tests.py`
