# TASK-145-01: Repair Planner Payload and Family Selection Policy

**Parent:** [TASK-145](./TASK-145_Spatial_Repair_Planner_And_Sculpt_Handoff_Context.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Depends On:** [TASK-122-03-07](./TASK-122-03-07_Deterministic_Cross_Domain_Refinement_Routing_And_Sculpt_Exposure.md), [TASK-143](./TASK-143_Guided_Spatial_Scope_And_Relation_Graphs.md), [TASK-144](./TASK-144_Camera_Aware_View_Graph_And_Visibility_Diagnostics.md)

## Objective

Turn the current `refinement_route` baseline into a stronger bounded
repair-planner contract that answers:

- which bounded family should own the next step
- which scope that family should act on
- which typed signals justified the choice
- which blockers still prevent a stronger handoff

without turning compare / iterate into another heavy default payload.

## Business Problem

Today the staged reference loop already has useful planner substrate:

- `assembled_target_scope`
- `truth_followup`
- `correction_candidates`
- `refinement_route`
- `budget_control`

But the current planner surface is still thin:

- `refinement_route` chooses a family, but not a fuller planner contract
- family selection still leans on coarse domain inference and limited inline
  reasoning
- existing scope / relation / visibility artifacts from TASK-143 / TASK-144
  do not yet have a clear planner-facing landing zone in the reference loop
- compare / iterate cannot simply absorb another large always-on payload

This subtask therefore needs to define a contract and policy layer that is
explicit enough for the LLM, but still small enough for the shaped guided
surface.

For the first implementation wave, that should mean **extending the current
`refinement_route` / `refinement_handoff` baseline first**, not opening a
second parallel planner family. If the existing contracts prove too narrow,
record the gap and promote a separate follow-on instead of expanding this
slice into a new flow.

## Technical Direction

Build the repair planner as a contract-and-policy upgrade over the current
`reference.py` flow:

- start from `_build_correction_candidates(...)`,
  `_select_refinement_route(...)`, and existing budget control
- extend the current `refinement_route` / `refinement_handoff` model before
  introducing any separate planner contract family
- keep provenance explicit across truth, macro, vision, scope, and future
  view/relation inputs
- define one compact inline planner summary plus one richer detail shape that
  can stay goal-aware / on-demand
- preserve the current bounded family vocabulary:
  - `macro`
  - `modeling_mesh`
  - `sculpt_region`
  - `inspect_only`
- keep planner logic deterministic and policy-driven; do not let it become an
  autonomous workflow engine

## Implementation Notes

- Treat `server/adapters/mcp/areas/reference.py` as the stage response
  assembler, not the long-term owner of complex planner policy.
- If family-selection or blocker rules become more than a small helper,
  extract them to `server/application/services/repair_planner.py` or an
  equivalent framework-free service/helper and call it from `reference.py`.
- If that extraction happens, keep the application service free of MCP adapter
  imports. It should return planner DTOs or framework-free policy results, and
  `server/adapters/mcp/areas/reference.py` should translate those results into
  `ReferenceRefinementRouteContract`, `ReferenceRefinementHandoffContract`, and
  any compact planner response fields.
- Keep scene truth ownership in `server/application/services/spatial_graph.py`
  and scene contracts. Planner policy consumes scope/relation/view evidence;
  it does not recalculate Blender truth.
- Staged compare / iterate must not treat current-view `view_diagnostics_hints`
  as present unless that evidence has actually been wired into the staged
  checkpoint response. Missing staged view evidence should become a typed
  blocker or an explicit request to run `scene_view_diagnostics(...)`.
- Any richer planner detail must be derived from the same evidence and policy
  result as the compact stage response. Do not create a separate planner
  session, persistence model, router flow, or LaBSE-backed planner.
- Names used in pseudocode such as `RepairPlannerEvidence`,
  `RepairPlannerDecision`, `repair_planner.select_next_family(...)`, and
  `planner_summary` are proposed implementation shapes, not existing public API.
  Implementers must either add them explicitly in the owning contract/service
  modules or map the same behavior onto the existing
  `ReferenceRefinementRouteContract` / `ReferenceRefinementHandoffContract`
  baseline without inventing a second flow.

## Pseudocode

```python
evidence = RepairPlannerEvidence(
    assembled_target_scope=compare.assembled_target_scope,
    truth_followup=compare.truth_followup,
    correction_candidates=compare.correction_candidates,
    # Only pass staged view evidence after the staged checkpoint path populates it.
    # Otherwise emit a typed blocker / required scene_view_diagnostics support call.
    view_diagnostics_hints=(
        compare.view_diagnostics_hints
        if compare.view_diagnostics_hints
        else None
    ),
    silhouette_analysis=compare.silhouette_analysis,
    action_hints=compare.action_hints,
    budget_control=compare.budget_control,
)

planner_result = repair_planner.select_next_family(evidence, goal=compare.goal)

compare.refinement_route = planner_result.route
compare.refinement_handoff = planner_result.handoff
compare.planner_summary = planner_result.compact_summary
```

## Repository Touchpoints

- `server/adapters/mcp/contracts/reference.py`
- `server/application/services/repair_planner.py` or equivalent policy helper
- `server/adapters/mcp/contracts/scene.py`
- `server/adapters/mcp/areas/reference.py`
- `server/application/services/spatial_graph.py`
- `server/application/tool_handlers/scene_handler.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `_docs/LLM_GUIDE_V2.md`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- planner output is a bounded, typed contract rather than a loose combination
  of route, handoff, and prose hints
- planner output preserves source provenance instead of collapsing truth /
  vision / macro / scope signals into one opaque score
- family selection can consume current `truth_followup` /
  `correction_candidates` plus existing TASK-143 / TASK-144 artifacts without
  duplicating those modules
- compare / iterate stay bounded:
  - no heavy new default planner payload
  - planner detail remains compact or on-demand
- planner policy remains a family selector / blocker model, not a new workflow
  engine

## Docs To Update

- `_docs/LLM_GUIDE_V2.md`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`

## Validation Category

- Unit contract and policy coverage must pass before this subtask closes.
- E2E coverage is required once the planner policy changes stage-loop runtime
  behavior or sculpt handoff behavior.
- Minimum targeted command for a contract-only slice:
  `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py -q`

## Changelog Impact

- add a `_docs/_CHANGELOG/*.md` entry when planner contract shape or
  family-selection policy ships

## Status / Board Update

- no board-count change is needed while TASK-145 remains the promoted open
  board item
- when this subtask is implemented and closed later, update parent/child
  statuses and the task board in the same allowed branch

## Execution Structure

| Order | Leaf | Status | Purpose |
|------|------|--------|---------|
| 1 | [TASK-145-01-01](./TASK-145-01-01_Planner_Envelope_And_Provenance_Contract.md) | ⏳ To Do | Define the bounded planner contract shape and provenance model on top of the current reference contracts |
| 2 | [TASK-145-01-02](./TASK-145-01-02_Deterministic_Family_Selection_From_Scope_Relation_And_View_Signals.md) | ⏳ To Do | Replace coarse planner selection with explicit deterministic precedence over scope, relation, truth, and view signals |
| 3 | [TASK-145-01-03](./TASK-145-01-03_Planner_Summary_Placement_And_Compare_Iterate_Budget_Gates.md) | ⏳ To Do | Place planner outputs into compare / iterate in a compact way with goal-aware disclosure and budget guards |
| 4 | [TASK-145-01-04](./TASK-145-01-04_Compact_Iterate_Response_Envelope_And_Debug_Payload_Split.md) | ✅ Done | Closed compact response debug split; stricter parity and E2E gates remain carried by [TASK-145-03-03](./TASK-145-03-03_Regression_Pack_For_Planner_And_Sculpt_Handoff.md) |
| 5 | [TASK-145-01-05](./TASK-145-01-05_Mesh_Aware_Organic_Seating_Repair_For_Rounded_Parts.md) | ✅ Done | Closed mesh-aware rounded seating slice; align warning/blocking, dependent-part guard, and Blender-backed proof remain carried by [TASK-145-03-03](./TASK-145-03-03_Regression_Pack_For_Planner_And_Sculpt_Handoff.md) |
