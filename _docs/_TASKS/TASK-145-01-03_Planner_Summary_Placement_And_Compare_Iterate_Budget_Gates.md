# TASK-145-01-03: Planner Summary Placement and Compare/Iterate Budget Gates

**Parent:** [TASK-145-01](./TASK-145-01_Repair_Planner_Payload_And_Family_Selection_Policy.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Depends On:** [TASK-145-01-01](./TASK-145-01-01_Planner_Envelope_And_Provenance_Contract.md), [TASK-145-01-02](./TASK-145-01-02_Deterministic_Family_Selection_From_Scope_Relation_And_View_Signals.md)

## Objective

Decide exactly where planner data lives in the staged reference loop so that:

- compare / iterate expose a compact planner summary
- richer planner detail is disclosed only when justified
- existing `budget_control` and trimming behavior stay authoritative

## Implementation Notes

- Compact compare / iterate responses may include a small planner summary, but
  must not embed full relation graphs, full truth bundles, or full candidate
  evidence by default.
- Rich/detail planner output must be derived from the same compare/iterate
  evidence and policy result. It must not require a new planner session or a
  second routing loop.
- `ReferenceHybridBudgetControlContract` remains the payload-size authority.
  Planner fields must participate in the same compact/rich budget rules.
- If a separate detail retrieval surface is introduced, it should be read-only,
  bounded, and backed by the current stage state.

## Pseudocode

```python
planner_summary = planner_result.to_compact_summary()
planner_detail = planner_result.to_detail() if include_detail else None

return _stage_compare_response(
    ...,
    refinement_route=planner_result.route,
    refinement_handoff=planner_result.handoff,
    planner_summary=planner_summary,
    planner_detail=planner_detail if preset_profile == "rich" else None,
    budget_control=budget_control.with_planner_counts(planner_result),
)
```

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/application/services/repair_planner.py` or equivalent policy helper
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`

## Acceptance Criteria

- planner summary placement is explicit in compare / iterate contracts
- default compare / iterate payload size does not regress into another heavy
  planner dump
- planner detail can expand in a goal-aware or handoff-aware way rather than
  staying fixed for every domain
- model-aware budget controls still trim scope/detail deterministically when
  needed

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/_PROMPTS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`

## Validation Category

- Unit coverage must fail if compact mode reintroduces full heavy planner or
  debug payloads.
- Targeted command:
  `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_structured_contract_delivery.py tests/unit/adapters/mcp/test_guided_surface_benchmarks.py -q`

## Changelog Impact

- include in the parent TASK-145 changelog entry when shipped

## Status / Board Update

- no board-count change is needed while TASK-145 remains the promoted open
  board item
