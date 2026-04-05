# TASK-132: Hybrid Budget, Mesh Overlap, and Guided Readiness Review Follow-Ups

**Status:** ✅ Done
**Priority:** 🔴 High
**Category:** Product Reliability / Review Follow-Up
**Estimated Effort:** Small
**Dependencies:** TASK-122-03-06, TASK-124, TASK-126
**Follow-on After:** [TASK-122-03-06](./TASK-122-03-06_Hybrid_Loop_Model_Aware_Budget_And_Scope_Control.md), [TASK-124](./TASK-124_Guided_Session_Goal_And_Reference_Orchestration.md), [TASK-126](./TASK-126_Mesh_Aware_Contact_Semantics_And_Visual_Fit_Reliability.md)

**Completion Summary:** Closed three narrow but important review findings
across the hybrid-loop/runtime truth path:

- Gemini model names such as `gemini-2.5-flash` / `gemini-2.5-pro` no longer
  hit the small-tier budget downgrade through the `gemini`/`mini` substring
  collision
- mesh-aware `scene_measure_gap(...)` now preserves real overlap detection
  instead of flattening overlapped mesh pairs into plain contact
- `guided_reference_readiness` no longer blocks a ready staged session just
  because explicit pending refs for another goal still exist

## Objective

Close the targeted review regressions that weakened:

- hybrid-loop budget control on Gemini backends
- mesh-aware overlap truth for contact assertions
- staged compare/iterate readiness on ready sessions with stale pending refs

## Business Problem

The branch had three correctness regressions in recently completed areas:

1. hybrid-loop model-name bias treated `gemini` as though it contained an
   explicit `mini` tier marker, trimming truth pairs/candidates too
   aggressively on Gemini compare flows
2. mesh-aware `measure_gap(...)` forced `bbox_overlap_volume=0.0` into the
   mesh path, so real overlaps could stop reporting `relation="overlapping"`
3. staged readiness blocked compare/iterate whenever *any* pending refs
   existed, even if they belonged to another goal and the active goal was
   already ready with attached refs

These were not redesign-level issues, but they did weaken trust in the truth
layer and guided staged-session behavior.

## Business Outcome

If these review follow-ups are closed correctly, the repo regains:

- stable model-aware hybrid-loop budgeting on Gemini backends
- trustworthy overlap rejection for mesh-aware contact assertions
- ready-session staged compare/iterate usability even when unrelated pending
  refs still exist elsewhere in the session state

## Scope

This follow-on covers:

- tightening the model-name bias token match in hybrid-loop budget control
- preserving true overlap propagation in mesh-aware `measure_gap(...)` and
  `assert_contact(...)`
- narrowing staged readiness blocking to goal-relevant pending refs only
- focused unit coverage plus concise docs/changelog updates for those three
  invariants

This follow-on does **not** cover:

- redesigning the broader hybrid-loop budget policy
- changing prompt-layer behavior or prompt recommendations
- changing pending-reference adoption rules for matching goals
- replacing the mesh-aware measurement path with a different geometry strategy

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/session_capabilities.py`
- `blender_addon/application/handlers/scene.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_session_phase.py`
- `tests/unit/tools/scene/test_scene_measure_tools.py`
- `tests/unit/tools/scene/test_scene_assert_tools.py`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/_CHANGELOG/README.md`
- `_docs/_TASKS/README.md`

## Acceptance Criteria

- Gemini model names are not downgraded by the `gemini`/`mini` substring
  collision; explicit small-tier names such as `-mini` still are
- mesh-aware `scene_measure_gap(...)` returns `relation="overlapping"` when the
  mesh path finds a true overlap, and `scene_assert_contact(..., allow_overlap=false)`
  still rejects that case
- `guided_reference_readiness.pending_reference_count` reflects only
  goal-relevant pending refs for the active staged session
- focused unit coverage proves all three regressions directly

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/_CHANGELOG/README.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_session_phase.py`
- `tests/unit/tools/scene/test_scene_measure_tools.py`
- `tests/unit/tools/scene/test_scene_assert_tools.py`

## Changelog Impact

- add one `_docs/_CHANGELOG/*` entry for this review-follow-up bundle

## Status / Board Update

- track this as a standalone completed follow-on on `_docs/_TASKS/README.md`
- keep the closed task lineage explicit through `Follow-on After`

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_session_phase.py tests/unit/tools/scene/test_scene_measure_tools.py tests/unit/tools/scene/test_scene_assert_tools.py -q`
