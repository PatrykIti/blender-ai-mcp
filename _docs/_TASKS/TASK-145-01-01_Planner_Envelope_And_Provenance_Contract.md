# TASK-145-01-01: Planner Envelope and Provenance Contract

**Parent:** [TASK-145-01](./TASK-145-01_Repair_Planner_Payload_And_Family_Selection_Policy.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Depends On:** [TASK-122-03-07](./TASK-122-03-07_Deterministic_Cross_Domain_Refinement_Routing_And_Sculpt_Exposure.md), [TASK-143](./TASK-143_Guided_Spatial_Scope_And_Relation_Graphs.md), [TASK-144](./TASK-144_Camera_Aware_View_Graph_And_Visibility_Diagnostics.md)

## Objective

Define one bounded repair-planner contract that can sit above the current
`refinement_route` / `refinement_handoff` baseline and explicitly carry:

- family selection
- repair scope
- planner rationale / provenance
- blocker and precondition slots
- compact-vs-detail placement rules

The intended v1 posture is incremental:

- extend the current `refinement_route` / `refinement_handoff` contracts first
- introduce a separate detail contract only if the existing route/handoff shape
  proves insufficient
- keep any detail contract as a read-only derivative of the current
  compare/iterate state, not as a new routing flow

## Implementation Notes

- The first pass should prefer additive fields on existing reference contracts
  over a new top-level planner flow.
- `ReferenceRefinementRouteContract`,
  `ReferenceRefinementHandoffContract`,
  `ReferenceCorrectionCandidateContract`, and
  `ReferenceHybridBudgetControlContract` are the existing owner contracts that
  should be extended or composed first.
- The envelope should preserve provenance by source class:
  - truth / relation graph evidence
  - macro candidate evidence
  - vision / silhouette advisory evidence
  - scope / anchor evidence
  - view/framing evidence
- Vision and silhouette evidence may explain why local-form refinement is worth
  considering, but they cannot mark a handoff ready when deterministic
  relation/view blockers remain unresolved.
- The `ReferenceRepairPlannerSummaryContract` and `ReferencePlanner*` names in
  the pseudocode below are candidate contract names for this leaf. They are not
  current repo symbols; the first implementation pass may instead extend the
  existing `ReferenceRefinementRouteContract` and
  `ReferenceRefinementHandoffContract` if that keeps the contract smaller.

## Pseudocode

```python
class ReferenceRepairPlannerSummaryContract(MCPContract):
    selected_family: Literal["macro", "modeling_mesh", "sculpt_region", "inspect_only"]
    target_scope: ReferencePlannerTargetScopeContract | None
    provenance: list[ReferencePlannerEvidenceSourceContract]
    blockers: list[ReferencePlannerBlockerContract] = []
    detail_available: bool = False


summary = ReferenceRepairPlannerSummaryContract(
    selected_family=route.selected_family,
    target_scope=derive_scope(compare.assembled_target_scope, candidates),
    provenance=collect_source_provenance(compare),
    blockers=derive_blockers(compare, route),
    detail_available=should_offer_detail(compare),
)
```

## Repository Touchpoints

- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/application/services/repair_planner.py` or equivalent policy helper
- `server/adapters/mcp/areas/reference.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Acceptance Criteria

- the planner contract is machine-readable and bounded
- provenance stays separated by source class such as truth, macro, vision,
  scope, and view rather than being flattened into one fuzzy explanation
- the contract makes room for TASK-143 relation/scope outputs and TASK-144
  visibility outputs without embedding those full graphs by default
- inline compare / iterate responses can expose a compact planner derivative
  while richer planner detail remains opt-in or separately retrievable
- the first planner wave does not open an unnecessary second planner abstraction
  if the current route/handoff contracts can be evolved instead
- any richer planner detail is clearly documented as an opt-in read-only
  derivative, not a second planner execution path

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/LLM_GUIDE_V2.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Validation Category

- Contract-only validation:
  `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_reference_images.py -q`
- No Blender E2E is required for pure schema work unless the implementation
  changes runtime handoff decisions.

## Changelog Impact

- include in the parent TASK-145 changelog entry when shipped

## Status / Board Update

- no board-count change is needed while TASK-145 remains the promoted open
  board item
