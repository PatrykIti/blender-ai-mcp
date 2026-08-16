# TASK-153-03-02: Transport Parity For Guided Runtime Visibility Authority

**Parent:** [TASK-153-03](./TASK-153-03_Regression_And_Docs_Closeout_For_Guided_Visibility_Authority.md)
**Depends On:** [TASK-153-03-01](./TASK-153-03-01_Unit_Regression_Matrix_For_Single_Runtime_Visibility_Authority.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Prove over real stdio and streamable guided sessions that `visibility_rules`,
`list_tools()`, and discovery/search all tell one coherent runtime story.

## Repository Touchpoints

- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Detailed Implementation Notes

- cover the full guided visibility lifecycle, not just one handoff point
- every transport scenario should explicitly compare at least two of:
  - `router_get_status().visibility_rules`
  - `list_tools()`
  - `search_tools(...)`
- use the existing patched server harnesses rather than inventing a separate
  transport fixture tree

## Planned File Change Map

- `tests/e2e/integration/test_guided_surface_contract_parity.py`
  - extend stdio scenarios across bootstrap, unlock, re-arm, and inspect
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
  - extend streamable scenarios with the same parity checks plus reconnect

## Pseudocode Sketch

```python
status = call_tool("router_get_status", {})
visible = {tool.name for tool in list_tools()}
search = {item["name"] for item in call_tool("search_tools", {"query": query})}

assert runtime_visible_subset(status["visibility_rules"]) == visible
assert blocked_tool not in search_before_unlock
assert blocked_tool in search_after_unlock
```

## Planned E2E / Transport Scenarios

- stdio:
  - bootstrap surface exposes only entry/discovery/spatial support tools
  - goal handoff keeps build tools hidden until `establish_spatial_context` is
    satisfied
  - spoofed `scene_view_diagnostics(target_object="Camera")` does not advance
  - real spatial scope unlocks `create_primary_masses`
  - role-gated build remains blocked without explicit role registration
  - spatial refresh re-arm hides secondary-part work until refresh completes
  - inspect/validate surface stays consistent across status/list/search
- streamable:
  - the same unlock/re-arm behavior works on the same session
  - reconnect/new-session reset restores the bounded default surface
  - search never leaks tools hidden by the current runtime state

## Acceptance Criteria

- stdio and streamable parity both prove a single runtime visibility authority

## Tests To Add/Update

- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Changelog Impact

- include in the parent TASK-153 changelog entry

## Completion Summary

- reran the guided stdio/streamable parity slice after the refactor and kept
  transport-backed visibility behavior aligned with the rule-driven model
