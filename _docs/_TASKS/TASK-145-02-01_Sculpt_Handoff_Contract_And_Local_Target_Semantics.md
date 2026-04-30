# TASK-145-02-01: Sculpt Handoff Contract and Local Target Semantics

**Parent:** [TASK-145-02](./TASK-145-02_Sculpt_Handoff_Context_And_Precondition_Model.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Depends On:** [TASK-145-01-01](./TASK-145-01-01_Planner_Envelope_And_Provenance_Contract.md)

## Objective

Define a sculpt handoff contract that makes explicit:

- selected family
- target object / local scope
- region or local-form reason
- bounded recommended tools and argument hints

instead of relying on the current minimal `object_name`-only handoff shape.

## Implementation Notes

- Extend or compose `ReferenceRefinementHandoffContract` before adding a new
  standalone sculpt-handoff family.
- Keep `_build_refinement_handoff(...)` aligned with the contract fields:
  target object, local scope, region/local-form reason, blockers, and bounded
  recommended tools.
- Argument hints must remain compatible with actual sculpt tool signatures in
  `server/adapters/mcp/areas/sculpt.py`; do not invent hidden arguments for the
  model-facing handoff.
- The handoff should describe recommendation readiness, not TASK-157 gate
  completion.

## Pseudocode

```python
if route.selected_family != "sculpt_region":
    return handoff_without_sculpt(route, blockers=planner_result.blockers)

return sculpt_handoff(
    target_scope=planner_result.target_scope,
    local_reason=planner_result.local_form_reason,
    recommended_tools=bounded_sculpt_region_tools,
    arguments_hint=derive_sculpt_arguments(planner_result.target_scope),
)
```

## Repository Touchpoints

- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/sculpt.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`

## Validation Category

- Targeted command:
  `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py -q`

## Acceptance Criteria

- the sculpt handoff clearly identifies the object or narrow local target that
  sculpt would act on
- the handoff includes an explicit local-form or region reason
- recommended tools remain bounded to the deterministic sculpt-region subset
- argument hints remain compatible with actual sculpt tool shapes in
  `server/adapters/mcp/areas/sculpt.py`

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`

## Changelog Impact

- include in the parent TASK-145 changelog entry when shipped

## Status / Board Update

- no board-count change is needed while TASK-145 remains the promoted open
  board item
