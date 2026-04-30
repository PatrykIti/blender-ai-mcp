# TASK-145-02-02: View, Relation, and Proportion Preconditions For Sculpt

**Parent:** [TASK-145-02](./TASK-145-02_Sculpt_Handoff_Context_And_Precondition_Model.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Depends On:** [TASK-145-02-01](./TASK-145-02-01_Sculpt_Handoff_Contract_And_Local_Target_Semantics.md), [TASK-143](./TASK-143_Guided_Spatial_Scope_And_Relation_Graphs.md), [TASK-144](./TASK-144_Camera_Aware_View_Graph_And_Visibility_Diagnostics.md)

## Objective

Encode the typed blockers that must be cleared before sculpt handoff becomes
valid, especially:

- unresolved attachment / support / overlap / contact failures
- missing visibility or poor framing for the intended region
- major proportion instability that still points back to macro or modeling

## Implementation Notes

- Treat `ready`, `blocked`, and suppression-style states as local handoff
  states only. Do not use them as TASK-157 quality-gate pass/fail statuses.
- Relation and view evidence should come from existing scope/relation/view
  artifacts rather than a new planner-specific truth pass.
- View evidence specifically should reuse
  `SceneToolHandler.get_view_diagnostics(...)`, `scene_view_diagnostics(...)`,
  and the current reference-loop `view_diagnostics_hints` call site; the sculpt
  precondition model should consume those facts instead of introducing a second
  camera/framing evaluator.
- If sculpt preconditions are evaluated from staged compare / iterate output,
  the task must first wire staged `view_diagnostics_hints` or require an
  explicit `scene_view_diagnostics(...)` support call. Do not treat current-view
  compare hints as if they already cover staged checkpoint responses.
- Sculpt remains blocked when deterministic relation evidence shows unresolved
  attachment, support, contact, or overlap failures.
- Proportion and silhouette signals may keep the decision on modeling/mesh or
  inspect-only, but cannot clear relation blockers.

## Pseudocode

```python
blockers = []
if relation_evidence.has_unresolved_structural_failure():
    blockers.append("relation_failure")
if view_evidence.target_not_visible_or_framed():
    blockers.append("view_precondition")
if proportion_evidence.requires_nonlocal_change():
    blockers.append("proportion_not_local")

return SculptHandoffPreconditions(
    state="ready" if not blockers else "blocked",
    blockers=blockers,
)
```

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/application/tool_handlers/scene_handler.py`
- `server/adapters/mcp/areas/scene.py`
- `server/application/services/repair_planner.py` or equivalent policy helper
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `tests/e2e/tools/sculpt/test_sculpt_tools.py`

## Validation Category

- Unit tests should cover each blocker independently and one positive
  ready-for-sculpt case.
- E2E is required when the implementation changes real stage-loop or Blender
  sculpt handoff behavior.

## Acceptance Criteria

- the handoff can distinguish `ready`, `blocked`, and similar bounded
  precondition states
- sculpt stays suppressed when structural relation failures still dominate
- visibility / framing requirements are explicit and derived from view-state
  facts rather than prompt prose alone
- staged sculpt readiness cannot read missing view evidence as `ready`; missing
  staged view evidence must become a typed blocker or a request for
  `scene_view_diagnostics(...)`
- major proportion drift can still keep the next step on macro/modeling even
  when the domain looks organic

## Docs To Update

- `_docs/LLM_GUIDE_V2.md`
- `_docs/_VISION/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `tests/e2e/tools/sculpt/test_sculpt_tools.py`

## Changelog Impact

- include in the parent TASK-145 changelog entry when shipped

## Status / Board Update

- no board-count change is needed while TASK-145 remains the promoted open
  board item
