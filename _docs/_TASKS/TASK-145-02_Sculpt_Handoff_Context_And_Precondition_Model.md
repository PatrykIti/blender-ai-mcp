# TASK-145-02: Sculpt Handoff Context and Precondition Model

**Parent:** [TASK-145](./TASK-145_Spatial_Repair_Planner_And_Sculpt_Handoff_Context.md)
**Status:** ⏳ To Do
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

This subtask should consume planner outputs from TASK-145-01 and the future
scope / relation / visibility artifacts from TASK-143 / TASK-144 without
duplicating their responsibilities.

## Repository Touchpoints

- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/sculpt.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/router/infrastructure/tools_metadata/sculpt/`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/e2e/tools/sculpt/test_sculpt_tools.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`

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

- add a `_docs/_CHANGELOG/*.md` entry when sculpt handoff contract or sculpt
  recommendation policy ships

## Status / Board Update

- planning-only execution-tree split: keep `_docs/_TASKS/README.md` unchanged
  in this branch
- when this subtask is implemented and closed later, update parent/child
  statuses and the task board in the same allowed branch

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-145-02-01](./TASK-145-02-01_Sculpt_Handoff_Contract_And_Local_Target_Semantics.md) | Define the sculpt handoff envelope, local target semantics, and bounded recommended-tool payload |
| 2 | [TASK-145-02-02](./TASK-145-02-02_View_Relation_And_Proportion_Preconditions_For_Sculpt.md) | Encode when sculpt is still blocked by structural, visibility, or proportion issues |
| 3 | [TASK-145-02-03](./TASK-145-02-03_Bounded_Sculpt_Metadata_And_Recommendation_Policy.md) | Align the handoff with actual sculpt metadata, search wording, and recommendation policy on the guided surface |
