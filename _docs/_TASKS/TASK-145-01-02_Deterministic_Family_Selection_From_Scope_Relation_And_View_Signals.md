# TASK-145-01-02: Deterministic Family Selection From Scope, Relation, and View Signals

**Parent:** [TASK-145-01](./TASK-145-01_Repair_Planner_Payload_And_Family_Selection_Policy.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Depends On:** [TASK-145-01-01](./TASK-145-01-01_Planner_Envelope_And_Provenance_Contract.md), [TASK-143](./TASK-143_Guided_Spatial_Scope_And_Relation_Graphs.md), [TASK-144](./TASK-144_Camera_Aware_View_Graph_And_Visibility_Diagnostics.md)

## Objective

Replace the current coarse family-selection heuristics with one deterministic
policy that evaluates:

- relation failures and macro evidence
- scope / anchor interpretation
- view visibility and framing constraints
- proportion stability and silhouette signals
- goal/domain context as a bias, not as the authority

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/contracts/scene.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `_docs/_VISION/CROSS_DOMAIN_REFINEMENT_ROUTING_EVAL.md`

## Acceptance Criteria

- macro remains the deterministic owner for unresolved attachment, support,
  contact, overlap, and similar relation failures
- sculpt is not selected while high-value structural blockers still dominate
- goal/domain tags can shape disclosure, but truth / relation / visibility
  signals remain the authority for family selection
- the selected family is explainable from typed planner sources and does not
  rely on a prompt-only classifier
- planner policy stays bounded to family selection / block reasons and does not
  expand into a free-form workflow planner

## Docs To Update

- `_docs/_VISION/CROSS_DOMAIN_REFINEMENT_ROUTING_EVAL.md`
- `_docs/_VISION/README.md`
- `_docs/LLM_GUIDE_V2.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `tests/e2e/vision/test_reference_guided_creature_comparison.py`

## Changelog Impact

- include in the parent TASK-145 changelog entry when shipped

## Status / Board Update

- no board change in this planning-only branch
