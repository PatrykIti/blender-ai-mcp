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

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/contracts/scene.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `tests/e2e/tools/sculpt/test_sculpt_tools.py`

## Acceptance Criteria

- the handoff can distinguish `ready`, `blocked`, and similar bounded
  precondition states
- sculpt stays suppressed when structural relation failures still dominate
- visibility / framing requirements are explicit and derived from view-state
  facts rather than prompt prose alone
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

- no board change in this planning-only branch
