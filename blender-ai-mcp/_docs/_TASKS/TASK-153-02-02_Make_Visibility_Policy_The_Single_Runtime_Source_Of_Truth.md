# TASK-153-02-02: Make Visibility Policy The Single Runtime Source Of Truth

**Parent:** [TASK-153-02](./TASK-153-02_Runtime_Visibility_Authority_Consolidation_For_LLM_Guided.md)
**Depends On:** [TASK-153-02-01](./TASK-153-02-01_Demote_Phase_Tags_From_LLM_Guided_Runtime_Gating.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Make `build_visibility_rules(...)` plus session state the single authority for
runtime exposure on `llm-guided`.

## Repository Touchpoints

- `server/adapters/mcp/guided_mode.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/transforms/visibility.py`
- `server/adapters/mcp/discovery/search_surface.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Current Code Anchors

- `guided_mode.py`
  - `build_visibility_diagnostics(...)`
  - `_is_capability_visible(...)`
- `visibility_policy.py`
  - `build_visibility_rules(...)`
- `visibility.py`
  - transform entrypoint for applied runtime visibility

## Planned Code Shape

```python
# diagnostics should report visibility derived from the same runtime rule model
runtime_rules = build_visibility_rules(...)
visible_tools = materialize_visible_tool_names(all_public_tool_names, runtime_rules)

# not:
visible_capabilities = manifest + tags + rules overlap
```

## Detailed Implementation Notes

- this is the core behavioral leaf for `TASK-153`
- the preferred implementation is to introduce one shared helper that answers:
  - which tool names are visible right now
  - which capabilities have at least one visible tool right now
- that helper should be consumed by:
  - `build_visibility_diagnostics(...)`
  - `search_surface.py` after session sync
  - any benchmark/parity tests that currently infer visibility indirectly
- do not maintain a separate guided-only shadow catalog

## Planned File Change Map

- `server/adapters/mcp/transforms/visibility_policy.py`
  - keep `build_visibility_rules(...)` authoritative
  - add any shared helper needed to materialize visible tool names
- `server/adapters/mcp/guided_mode.py`
  - rebuild diagnostics from the shared runtime helper
- `server/adapters/mcp/transforms/visibility.py`
  - ensure bootstrap transforms still reflect the shared runtime policy
- `server/adapters/mcp/discovery/search_surface.py`
  - filter discovery results only against the synced visible tool set
- `tests/unit/adapters/mcp/test_visibility_policy.py`
  - assert the shared helper/rules behave deterministically
- `tests/unit/adapters/mcp/test_guided_mode.py`
  - assert diagnostics agree with the runtime helper
- `tests/unit/adapters/mcp/test_search_surface.py`
  - assert search honors the current visible set across phase transitions
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
  - assert guided surface counts remain intentional after the single-source
    refactor
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
  - extend stdio parity to compare `visibility_rules`, `list_tools()`, and
    discovery results on the same session timeline
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
  - extend streamable parity with the same single-source assertions

## Pseudocode Sketch

```python
def build_visibility_diagnostics(...):
    runtime_rules = build_visibility_rules(...)
    visible_tool_names = materialize_visible_tool_names(all_public_tool_names, runtime_rules)

    visible_capability_ids = tuple(
        entry.capability_id
        for entry in get_capability_manifest()
        if set(entry.tool_names).intersection(visible_tool_names)
    )

    return VisibilityDiagnostics(
        rules=tuple(runtime_rules),
        visible_capability_ids=visible_capability_ids,
        ...
    )
```

## Planned Unit Test Scenarios

- `router_get_status().visibility_rules` and `list_tools()` stay consistent
- search/discovery does not surface tools hidden by runtime visibility
- inspect/build phase tool counts remain stable under the single-source model
- capability visibility is computed from visible tool membership, not from
  phase-tag overlap

## Planned E2E Scenarios

- stdio guided session:
  - bootstrap `list_tools()` stays bounded to the small entry/discovery layer
  - after goal handoff, `router_get_status().visibility_rules` still agrees
    with the direct visible surface
  - after satisfying the spatial step, build tools unlock in both
    `router_get_status()` and `search_tools(...)`
  - after re-arm, blocked secondary tools stay hidden until spatial refresh
- streamable guided session:
  - same parity assertions survive transport/session synchronization
  - reconnect/new-session reset restores the default bounded surface

## Acceptance Criteria

- runtime visibility/listing/discovery all derive from one coherent rule path

## Docs To Update

- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Changelog Impact

- include in the parent TASK-153 changelog entry

## Completion Summary

- added `materialize_visible_tool_names(...)` as the shared rule-driven helper
- rebuilt guided capability diagnostics from runtime-visible tool membership
  instead of manifest/tag overlap inference
