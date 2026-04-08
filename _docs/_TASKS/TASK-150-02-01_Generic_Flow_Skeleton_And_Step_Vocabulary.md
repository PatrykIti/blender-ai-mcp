# TASK-150-02-01: Generic Flow Skeleton And Step Vocabulary

**Parent:** [TASK-150-02](./TASK-150-02_Domain_Profile_Selection_And_Overlay_Policy.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Define the generic server-driven guided flow skeleton and one shared step
vocabulary that all domain overlays build on.

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/session_phase.py`
- `server/adapters/mcp/contracts/router.py`
- `_docs/_PROMPTS/README.md`

## Planned File Work

- Modify:
  - `server/adapters/mcp/session_capabilities.py`
  - `server/adapters/mcp/contracts/router.py`
  - `_docs/_PROMPTS/README.md`

## Detailed Implementation Notes

- keep the generic step vocabulary stable and intentionally small
- prefer names that can work for creature and building overlays without being
  misleadingly domain-specific
- the generic skeleton should express sequencing, not tool names directly
- later leaves can map steps to tools/prompts/checks

## Planned Test Files And Scenarios

- Modify `tests/unit/adapters/mcp/test_session_phase.py`
  - step vocabulary remains stable
  - generic flow initialization uses one valid baseline step
- Modify `tests/unit/adapters/mcp/test_contract_payload_parity.py`
  - generic flow contract includes valid step names only

## Example Step Vocabulary Draft

```text
1. understand_goal
2. establish_spatial_context
3. establish_reference_context
4. create_primary_masses
5. place_secondary_parts
6. checkpoint_iterate
7. inspect_validate
8. finish_or_stop
```

## Acceptance Criteria

- the repo has one generic flow skeleton before domain specialization
- step names are explicit and reusable
- step vocabulary is not creature-specific

## Pseudocode Sketch

```python
GENERIC_GUIDED_STEPS = (
    "understand_goal",
    "establish_spatial_context",
    "create_primary_masses",
    "place_secondary_parts",
    "checkpoint_iterate",
    "inspect_validate",
)

def initialize_guided_flow_state(...):
    return GuidedFlowState(
        flow_id="guided_default",
        domain_profile="generic",
        current_step="establish_spatial_context",
        completed_steps=(),
        required_checks=("scene_scope_graph", "scene_relation_graph", "scene_view_diagnostics"),
        ...
    )
```

## Docs To Update

- `_docs/_PROMPTS/README.md`

## Tests To Add/Update

- contract/state tests as needed under `tests/unit/adapters/mcp/`

## Changelog Impact

- include in the parent TASK-150 changelog entry when shipped
