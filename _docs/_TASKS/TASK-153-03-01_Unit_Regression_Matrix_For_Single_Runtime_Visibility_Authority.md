# TASK-153-03-01: Unit Regression Matrix For Single Runtime Visibility Authority

**Parent:** [TASK-153-03](./TASK-153-03_Regression_And_Docs_Closeout_For_Guided_Visibility_Authority.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Build the unit regression matrix that proves runtime visibility, diagnostics,
search, inventory, and factory metadata all follow the same post-refactor
contract.

## Repository Touchpoints

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`
- `tests/unit/adapters/mcp/test_surface_inventory.py`
- `tests/unit/adapters/mcp/test_server_factory.py`

## Detailed Implementation Notes

- keep this matrix split by behavior seam, not by file ownership
- each assertion should answer one of two questions:
  - is runtime visibility still driven by the same rule set everywhere?
  - is manifest/tag metadata still useful without becoming a runtime gate?

## Planned File Change Map

- `tests/unit/adapters/mcp/test_visibility_policy.py`
  - assert the authoritative runtime rule/materialization path
- `tests/unit/adapters/mcp/test_guided_mode.py`
  - assert diagnostics mirror the runtime visible set
- `tests/unit/adapters/mcp/test_search_surface.py`
  - assert search respects the synced visible set across phase transitions
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
  - assert tool-count/payload baselines remain intentional
- `tests/unit/adapters/mcp/test_provider_inventory.py`
  - assert provider groups and public surface registration remain stable
- `tests/unit/adapters/mcp/test_tool_inventory.py`
  - assert aliases, pinned tools, and metadata enrichment remain stable
- `tests/unit/adapters/mcp/test_surface_inventory.py`
  - assert the shared manifest scaffold still exists on built surfaces
- `tests/unit/adapters/mcp/test_server_factory.py`
  - assert server bootstrap metadata still reflects the manifest scaffold

## Pseudocode Sketch

```python
rules = build_visibility_rules("llm-guided", SessionPhase.BUILD, guided_flow_state=flow_state)
visible_tool_names = materialize_visible_tool_names(all_public_tool_names, rules)
diagnostics = build_visibility_diagnostics("llm-guided", SessionPhase.BUILD, guided_flow_state=flow_state)

assert set(diagnostics.visible_capability_ids) == capabilities_from_visible_tools(visible_tool_names)
assert "modeling_create_primitive" not in search_results_before_unlock
assert "modeling_create_primitive" in search_results_after_unlock
```

## Planned Unit Test Scenarios

- visibility policy:
  - phase-tag demotion does not alter the intended runtime rule output
  - any shared visible-tool helper stays deterministic across bootstrap/build/inspect
- guided diagnostics:
  - visible capability ids are derived from visible tools, not from phase-tag
    overlap
- search surface:
  - hidden tools are not discoverable before unlock
  - unlocked tools become discoverable immediately after the relevant state
    transition
- benchmarks:
  - bootstrap/build/inspect footprints remain intentionally bounded
- metadata/inventory:
  - provider groups, aliases, categories, pinned tools, and manifest snapshots
    remain stable after demotion

## Acceptance Criteria

- unit coverage proves there is no second hidden runtime visibility authority
- unit coverage proves the manifest remains useful as metadata

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`
- `tests/unit/adapters/mcp/test_surface_inventory.py`
- `tests/unit/adapters/mcp/test_server_factory.py`

## Changelog Impact

- include in the parent TASK-153 changelog entry

## Completion Summary

- added/updated unit coverage for:
  - coarse tags plus metadata-only phase hints
  - rule-driven visible-tool materialization
  - guided diagnostics parity
  - manifest/discovery/factory metadata preservation
