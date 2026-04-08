# TASK-150-03-01: Flow-Aware Visibility Rules And Search-Surface Gating

**Parent:** [TASK-150-03](./TASK-150-03_Step_Gated_Visibility_And_Execution_Policy.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Make visibility rules and the shaped search surface consult guided flow step
and domain profile, not only coarse phase.

## Repository Touchpoints

- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/guided_mode.py`
- `server/adapters/mcp/discovery/search_surface.py`
- `server/adapters/mcp/platform/capability_manifest.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`

## Planned File Work

- Modify:
  - `server/adapters/mcp/transforms/visibility_policy.py`
  - `server/adapters/mcp/guided_mode.py`
  - `server/adapters/mcp/discovery/search_surface.py`
  - `server/adapters/mcp/platform/capability_manifest.py`
  - `tests/unit/adapters/mcp/test_visibility_policy.py`
  - `tests/unit/adapters/mcp/test_search_surface.py`

## Detailed Implementation Notes

- add `guided_flow_state` as an optional input to visibility rule building
- keep the current `SessionPhase` model as the outer coarse partition, but let
  flow step refine what is actually visible/searchable inside a phase
- keep direct `tools/list` and search/call parity aligned:
  - if a tool family is blocked by flow step, it should not show up as a
    directly visible tool
  - and should not become effectively callable through a search/call bypass

## Planned Test Files And Scenarios

- Modify `tests/unit/adapters/mcp/test_visibility_policy.py`
  - flow-step-specific build rules
  - flow-step-specific inspect rules
  - overlay-specific visibility differences
- Modify `tests/unit/adapters/mcp/test_search_surface.py`
  - search results follow flow-step gating
  - pinned direct tools remain bounded
  - hidden families do not leak through search
- Create `tests/unit/adapters/mcp/test_guided_flow_visibility.py` if needed
  - dedicated matrix for `phase x domain_profile x current_step`

## Example Test Sketch

```python
def test_creature_flow_primary_masses_step_hides_finish_family():
    rules = build_visibility_rules(
        "llm-guided",
        SessionPhase.BUILD,
        guided_flow_state={"domain_profile": "creature", "current_step": "create_primary_masses"},
    )
    assert "macro_finish_form" not in visible_tool_names(rules)
```

## Acceptance Criteria

- visibility rules can depend on `guided_flow_state.current_step`
- search/call behavior stays aligned with the same flow-aware visibility
- the shaped surface remains bounded even with step-aware disclosure

## Pseudocode Sketch

```python
def build_visibility_rules(surface_profile, phase, guided_handoff=None, guided_flow_state=None):
    rules = bootstrap_rules(...)
    if guided_flow_state:
        step = guided_flow_state["current_step"]
        domain = guided_flow_state["domain_profile"]
        rules.extend(FLOW_STEP_RULES[domain][step])
    return rules
```

## Docs To Update

- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`

## Changelog Impact

- include in the parent TASK-150 changelog entry when shipped
