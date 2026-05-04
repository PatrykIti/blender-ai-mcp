# TASK-145-02: Sculpt Handoff Context and Precondition Model

**Parent:** [TASK-145](./TASK-145_Spatial_Repair_Planner_And_Sculpt_Handoff_Context.md)
**Status:** ✅ Done
**Priority:** 🔴 High
**Depends On:** [TASK-145-01](./TASK-145-01_Repair_Planner_Payload_And_Family_Selection_Policy.md), [TASK-143](./TASK-143_Guided_Spatial_Scope_And_Relation_Graphs.md), [TASK-144](./TASK-144_Camera_Aware_View_Graph_And_Visibility_Diagnostics.md)

## Objective

Upgrade the current recommendation-only sculpt handoff from "selected family
plus tool list" into a bounded local-context contract that answers:

- what local scope sculpt would operate on
- why sculpt is justified here
- which relation / visibility / proportion preconditions are still required
- which deterministic sculpt-region tools remain allowed

## Business Problem

The current code already has a safe first sculpt story:

- `_select_refinement_route(...)` can choose `sculpt_region`
- `_build_refinement_handoff(...)` recommends a small deterministic sculpt set
- `llm-guided` still keeps sculpt hidden by default

But the current handoff is still too shallow for reliable use:

- it usually only carries `object_name`
- it does not explain the local reason or intended region semantics
- it does not tell the model when sculpt is still blocked by attachment,
  visibility, or proportion instability
- it does not clearly distinguish recommendation-only handoff from a general
  "you can sculpt now" surface unlock

## Technical Direction

Keep the first product posture conservative:

- sculpt remains bounded and recommendation-oriented by default
- preconditions are expressed as typed planner / handoff state
- current deterministic sculpt-region tools stay the primary eligible subset
- brush/setup flows and broad whole-mesh sculpt paths do not become the normal
  guided handoff

This subtask should consume planner outputs from TASK-145-01 and the existing
scope / relation / visibility artifacts from TASK-143 / TASK-144 without
duplicating their responsibilities.

## Implementation Notes

- `ReferenceRefinementHandoffContract`, `_SCULPT_RECOMMENDED_TOOLS`, and
  `_build_refinement_handoff(...)` are the current recommendation owners and
  must move together with sculpt metadata/search wording.
- Sculpt handoff state is not a TASK-157 quality-gate status. It may report
  local readiness, blockers, and suppressions, but final gate pass/fail and
  completion blocking remain TASK-157 responsibilities.
- The handoff should consume deterministic relation/view evidence before
  recommending sculpt. Vision/silhouette evidence may support a local-form
  recommendation, but cannot clear structural blockers.
- Broad brush/setup flows and whole-mesh sculpting should stay out of the
  normal guided handoff unless a later task explicitly promotes them.
- `build_sculpt_handoff(...)`, `planner_result.target_scope`, and
  `safe_fallback_family` in the pseudocode are proposed helper/result fields.
  They must be implemented explicitly or mapped onto the current
  `ReferenceRefinementHandoffContract` / planner-policy result without creating
  a standalone sculpt planner state.

## Pseudocode

```python
handoff = build_sculpt_handoff(
    route=planner_result.route,
    target_scope=planner_result.target_scope,
    blockers=planner_result.blockers,
    recommended_tools=bounded_sculpt_region_tools,
)

if handoff.has_blockers:
    handoff.selected_family = planner_result.safe_fallback_family
    handoff.recommended_tools = []
```

## Repository Touchpoints

- `server/adapters/mcp/contracts/reference.py`
- `server/application/services/repair_planner.py` or equivalent policy helper
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/sculpt.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/router/infrastructure/tools_metadata/sculpt/`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/e2e/tools/sculpt/test_sculpt_tools.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`

## Validation Category

- Unit reference tests must cover both ready and blocked sculpt handoff.
- Visibility tests must prove `llm-guided` does not expose the full sculpt
  family by default.
- Targeted unit lane:
  `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_visibility_policy.py -q`
- Blender E2E is required when tool arguments or real sculpt behavior change.
- Targeted E2E lane when runtime sculpt behavior changes:
  `poetry run pytest tests/e2e/vision/test_reference_stage_truth_handoff.py tests/e2e/tools/sculpt/test_sculpt_tools.py -q`
- Docs/preflight:
  `git diff --check`

## Acceptance Criteria

- sculpt handoff is a typed bounded contract, not just a list of suggested
  tools
- the handoff makes explicit the local scope / target and the reason sculpt is
  appropriate
- unresolved relation, visibility, or proportion blockers can suppress or
  downgrade sculpt handoff deterministically
- the eligible sculpt subset remains narrow and aligned with deterministic
  region tools rather than broad whole-surface or brush/setup flows
- `llm-guided` stays small and does not auto-expose the whole sculpt family by
  default

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/LLM_GUIDE_V2.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `tests/e2e/tools/sculpt/test_sculpt_tools.py`

## Changelog Impact

- covered by [_docs/_CHANGELOG/276-2026-04-30-task-145-repair-planner-handoff.md](../_CHANGELOG/276-2026-04-30-task-145-repair-planner-handoff.md)

## Completion Summary

Closed by making `ReferenceRefinementHandoffContract` carry bounded local
target semantics, `ready` / `blocked` / `suppressed` state, typed blockers,
eligible sculpt tools, and recommendation-only visibility metadata. Missing or
blocking staged view evidence now suppresses sculpt and asks for
`scene_view_diagnostics(...)`; `sculpt_crease_region` is consciously included in
the deterministic region subset.

## Status / Board Update

- closed under the completed TASK-145 umbrella
- no separate board row is needed because TASK-145 remains the promoted item

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-145-02-01](./TASK-145-02-01_Sculpt_Handoff_Contract_And_Local_Target_Semantics.md) | Define the sculpt handoff envelope, local target semantics, and bounded recommended-tool payload |
| 2 | [TASK-145-02-02](./TASK-145-02-02_View_Relation_And_Proportion_Preconditions_For_Sculpt.md) | Encode when sculpt is still blocked by structural, visibility, or proportion issues |
| 3 | [TASK-145-02-03](./TASK-145-02-03_Bounded_Sculpt_Metadata_And_Recommendation_Policy.md) | Align the handoff with actual sculpt metadata, search wording, and recommendation policy on the guided surface |
