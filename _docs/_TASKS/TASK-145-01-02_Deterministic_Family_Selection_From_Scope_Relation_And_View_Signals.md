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
- goal/domain context as a bias, not as evidence authority

## Implementation Notes

- Treat truth/relation/view outputs as evidence and constraints. The planner
  policy chooses the next bounded family; evidence contracts do not themselves
  become an autonomous workflow.
- Macro remains the default owner for unresolved structural relation failures
  such as attachment, support, contact, and overlap.
- Sculpt can be selected only when structural blockers are absent or explicitly
  downgraded, the local target is known, and visibility/framing is adequate for
  a bounded local-form edit.
- Vision/silhouette signals may recommend inspection, local-form attention, or
  downranking/upgrading priority, but they cannot override deterministic
  relation truth or mark sculpt ready on their own.
- Keep policy deterministic and testable. Avoid prompt-only classifiers,
  LaBSE matching, or free-form planner text as the source of family selection.

## Pseudocode

```python
def select_next_family(evidence: RepairPlannerEvidence) -> RepairPlannerDecision:
    if evidence.has_unresolved_relation_failure(
        kinds={"attachment", "support", "contact", "overlap"}
    ):
        return macro_decision(reason="relation_failure_blocks_sculpt")

    if evidence.view_is_missing_or_unstable():
        return inspect_decision(reason="view_precondition_missing")

    if evidence.proportion_drift_requires_mesh_or_macro():
        return modeling_decision(reason="proportion_not_local_sculpt")

    if evidence.local_organic_form_signal() and evidence.has_local_target():
        return sculpt_region_decision(reason="bounded_local_form_refinement")

    return modeling_decision(reason="safe_default_family")
```

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/application/services/repair_planner.py` or equivalent policy helper
- `server/application/services/spatial_graph.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `_docs/_VISION/CROSS_DOMAIN_REFINEMENT_ROUTING_EVAL.md`

## Acceptance Criteria

- macro remains the deterministic owner for unresolved attachment, support,
  contact, overlap, and similar relation failures
- sculpt is not selected while high-value structural blockers still dominate
- goal/domain tags can shape disclosure, but deterministic evidence and
  planner policy remain the source of the family-selection decision
- vision/silhouette signals stay advisory and cannot override unresolved
  relation blockers
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

## Validation Category

- Unit policy coverage should assert at least:
  - unresolved relation failure selects `macro`
  - poor view/framing selects `inspect_only` or blocks sculpt
  - low-poly/proportion drift stays on `modeling_mesh`
  - organic local-form signal selects `sculpt_region` only after blockers clear
- Targeted command:
  `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`

## Changelog Impact

- include in the parent TASK-145 changelog entry when shipped

## Status / Board Update

- no board-count change is needed while TASK-145 remains the promoted open
  board item
