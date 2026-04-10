# TASK-153-02: Runtime Visibility Authority Consolidation For LLM Guided

**Parent:** [TASK-153](./TASK-153_Guided_Visibility_Authority_And_Manifest_Demotion.md)
**Depends On:** [TASK-153-01](./TASK-153-01_Responsibility_Split_For_Capability_Metadata_And_Runtime_Visibility.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Refactor `llm-guided` so runtime exposure/listing/discovery is driven by one
authority path instead of overlapping metadata-plus-policy gates.

## Detailed Implementation Notes

- this subtask owns runtime behavior, not just wording
- the refactor should converge the following views onto the same active rule
  model:
  - FastMCP tool visibility (`list_tools()`)
  - `router_get_status().visibility_rules`
  - guided-mode diagnostics
  - search/discovery filtering after session sync
- prefer extending the current `visibility_policy.py` and `guided_mode.py`
  helpers over introducing a second runtime catalog
- manifest and capability tags should remain available to the discovery layer,
  but they must stop being an implicit second gate for `llm-guided`

## Repository Touchpoints

- `server/adapters/mcp/visibility/tags.py`
- `server/adapters/mcp/platform/capability_manifest.py`
- `server/adapters/mcp/guided_mode.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/transforms/visibility.py`
- `server/adapters/mcp/discovery/tool_inventory.py`
- `server/adapters/mcp/discovery/search_surface.py`
- `server/adapters/mcp/factory.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`
- `tests/unit/adapters/mcp/test_surface_inventory.py`
- `tests/unit/adapters/mcp/test_server_factory.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Planned File Change Map

- `server/adapters/mcp/visibility/tags.py`
  - edit runtime-facing capability tags so they stop carrying hidden phase
    authority for `llm-guided`
- `server/adapters/mcp/platform/capability_manifest.py`
  - preserve manifest value for provider/discovery metadata after phase-tag
    demotion
- `server/adapters/mcp/guided_mode.py`
  - derive capability visibility and diagnostics from the same runtime rule
    application used by the actual surface
- `server/adapters/mcp/transforms/visibility_policy.py`
  - keep the single runtime rule builder and expose any shared materialization
    helpers needed by diagnostics/search
- `server/adapters/mcp/transforms/visibility.py`
  - keep transform application aligned with the same shared rule semantics
- `server/adapters/mcp/discovery/tool_inventory.py`
  - keep inventory phase-agnostic and metadata-driven
- `server/adapters/mcp/discovery/search_surface.py`
  - ensure search stays bounded to the current runtime-visible set after sync
- `server/adapters/mcp/factory.py`
  - keep manifest bootstrap metadata explicit while not implying runtime gating
- tests
  - update unit, benchmark, and transport parity coverage around the single
    runtime authority

## Acceptance Criteria

- tags/manifest no longer act as a second hidden runtime phase gate on
  `llm-guided`
- `router_get_status().visibility_rules`, `list_tools()`, and discovery/search
  tell one consistent story
- metadata remains available for inventory/discovery/provider wiring

## Planned Validation Matrix

- unit / runtime source of truth:
  - phase-tag demotion does not re-open hidden tools or hide allowed tools
  - guided diagnostics and benchmark counts reflect the same visible tool set as
    `list_tools()`
  - `search_tools(...)` respects unlocks, re-arms, and inspect-phase shifts
- unit / metadata preservation:
  - provider groups, aliases, pinned tools, and discovery categories remain
    stable
  - factory/bootstrap manifest snapshots remain stable
- E2E / transport:
  - stdio and streamable guided sessions show the same runtime authority during:
    - bootstrap
    - goal handoff
    - spatial unlock
    - role-gated build
    - spatial refresh re-arm
    - inspect/validate
    - reconnect/new-session reset

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-153-02-01](./TASK-153-02-01_Demote_Phase_Tags_From_LLM_Guided_Runtime_Gating.md) | Remove or demote phase-tag participation in `llm-guided` runtime gating |
| 2 | [TASK-153-02-02](./TASK-153-02-02_Make_Visibility_Policy_The_Single_Runtime_Source_Of_Truth.md) | Make runtime visibility/listing/discovery derive from the same visibility-policy authority |
| 3 | [TASK-153-02-03](./TASK-153-02-03_Keep_Manifest_Metadata_Useful_Without_Runtime_Gating.md) | Preserve capability manifest value for discovery/inventory/docs without phase-gating runtime exposure |

## Docs To Update

- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`
- `tests/unit/adapters/mcp/test_surface_inventory.py`
- `tests/unit/adapters/mcp/test_server_factory.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Changelog Impact

- include in the parent TASK-153 changelog entry
