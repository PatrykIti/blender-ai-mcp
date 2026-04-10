# TASK-153-03: Regression And Docs Closeout For Guided Visibility Authority

**Parent:** [TASK-153](./TASK-153_Guided_Visibility_Authority_And_Manifest_Demotion.md)
**Depends On:** [TASK-153-01](./TASK-153-01_Responsibility_Split_For_Capability_Metadata_And_Runtime_Visibility.md), [TASK-153-02](./TASK-153-02_Runtime_Visibility_Authority_Consolidation_For_LLM_Guided.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Lock in the single-authority visibility architecture with regression tests,
benchmarks, docs, and changelog closeout.

## Repository Touchpoints

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`
- `tests/unit/adapters/mcp/test_surface_inventory.py`
- `tests/unit/adapters/mcp/test_server_factory.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_CHANGELOG/README.md`
- `_docs/_TASKS/README.md`

## Acceptance Criteria

- regression tests prove there is no second hidden runtime visibility policy on
  `llm-guided`
- docs explain the new responsibility split clearly
- board/changelog/docs are updated in the same branch when TASK-153 ships

## Detailed Implementation Notes

- this subtask should not invent new runtime semantics
- it exists to prove and document the behavior implemented in `TASK-153-02`
- closeout is only complete when:
  - unit regressions cover every changed runtime seam
  - stdio and streamable parity cover every guided transition touched by the
    refactor
  - operator/public docs state the same architecture the tests enforce
  - changelog and board state are updated together when the parent task closes

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-153-03-01](./TASK-153-03-01_Unit_Regression_Matrix_For_Single_Runtime_Visibility_Authority.md) | Build the unit regression matrix around visibility policy, diagnostics, search, inventory, and factory metadata |
| 2 | [TASK-153-03-02](./TASK-153-03-02_Transport_Parity_For_Guided_Runtime_Visibility_Authority.md) | Prove stdio and streamable guided sessions tell one coherent runtime visibility story end to end |
| 3 | [TASK-153-03-03](./TASK-153-03-03_Docs_And_Historical_Closeout_For_Guided_Visibility_Authority.md) | Align docs, docs parity tests, board state, and changelog/history once the runtime work lands |

## Planned Validation Matrix

- unit / visibility semantics:
  - no tag-only hidden phase gate remains
  - diagnostics, search, and benchmarks match the actual visible tool set
- unit / metadata semantics:
  - manifest/inventory/factory metadata stays useful and phase-agnostic
- transport / stdio:
  - bootstrap -> goal handoff -> spatial unlock -> role gating ->
    spatial refresh -> inspect/validate
- transport / streamable:
  - same runtime authority as stdio plus reconnect/new-session reset coverage
- docs/history:
  - runtime-vs-metadata split documented
  - changelog entry added
  - board/task docs updated together when the parent closes

## Docs To Update

- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_CHANGELOG/README.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`
- `tests/unit/adapters/mcp/test_surface_inventory.py`
- `tests/unit/adapters/mcp/test_server_factory.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when TASK-153 ships

## Completion Summary

- completed the unit regression matrix around visibility rules, diagnostics,
  discovery, inventory, and factory metadata
- verified transport parity on the guided stdio/streamable surface slice
- updated docs, board state, and changelog together with the shipped runtime
  behavior
