# TASK-186-03: Part Naming And Guided Register Part Integration

**Parent:** [TASK-186](./TASK-186_Semantic_Part_Decomposition_And_Registry_Materialization.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Normalize decomposed part names and register materialized parts through the existing guided part registry instead of inventing a parallel registration surface.

**Repository Touchpoints:** `server/adapters/mcp/areas/`, `server/adapters/mcp/contracts/`, current guided part registry modules, `tests/unit/adapters/mcp/`, `tests/e2e/integration/`

## Implementation Notes

- Reuse existing guided part registry contracts and state keys.
- Normalize names through the repo naming policy before registration.
- Preserve provider/source labels separately from canonical object names.
- Register only materialized, inspectable parts; advisory-only hypotheses stay
  in support evidence.

## Runtime / Security Contract Notes

- registration is guided-session state mutation and must preserve auth/session
  assumptions already used by guided mode
- duplicate names, stale object references, and unresolved source assets must
  return meaningful errors

## Tests To Add/Update

- unit tests for name normalization and duplicate handling
- registry integration tests for materialized part refs
- E2E guided transport test if the public/guided surface changes

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md` if any public surface changes

## Acceptance Criteria

- decomposed parts use the existing registry path
- provider labels do not overwrite canonical object names
- downstream relation graph/compare scope can see the registered parts

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp -q`
