# TASK-128-02: Deterministic Silhouette Analysis and Typed Action Hints

**Parent:** [TASK-128](./TASK-128_Reference_Guided_Creature_Build_Surface_And_Perception_Reliability.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Add a deterministic silhouette-analysis layer that turns reference/viewport
shape comparison into machine-readable metrics and typed corrective
`action_hints`, instead of relying only on prose mismatch summaries.

## Business Problem

The current hybrid loop already gives:

- `shape_mismatches`
- `proportion_mismatches`
- `correction_focus`
- `next_corrections`
- ranked `correction_candidates`

That is useful, but still too descriptive for precise creature shaping.
Low-poly and early organic blockout need measurable signals such as:

- silhouette mask overlap
- contour drift
- width-profile deltas
- ear height / ear base width
- snout length / snout drop
- tail arc height

This slice should introduce those signals without violating the current
boundaries:

- perception interprets masks and metrics
- truth still owns scene correctness
- router still owns policy

## Business Outcome

If this slice is done correctly:

- the loop gets deterministic shape evidence in addition to prose
- `reference_iterate_stage_checkpoint(...)` can surface typed next-tool hints
- creature blockout gains a better path for "profile this more precisely"
  requests
- later segmentation work has a stable contract to plug into

## Scope

This slice covers:

- silhouette-analysis contract and response placement
- reference/viewport mask extraction and alignment planning
- contour/ratio/width-profile metric bundles
- typed `action_hints` planning for iterate-stage output
- docs/regression planning for the new perception layer

This slice does **not** cover:

- SAM 3 or Grounding DINO integration
- making silhouette metrics the truth layer
- router-side image analysis

## Acceptance Criteria

- the repo has one explicit contract for silhouette/perception outputs
- the planned metric bundle covers both global silhouette and targeted
  creature-form ratios
- `reference_iterate_stage_checkpoint(...)` has a planned typed
  `action_hints` path that complements, but does not replace,
  `correction_candidates`
- docs/tests describe the new prioritization order between perception hints,
  correction candidates, and truth follow-up

## Repository Touchpoints

- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/vision/`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_vision_*`
- `tests/e2e/vision/`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- focused `tests/unit/adapters/mcp/test_vision_*` coverage
- `tests/e2e/vision/` once the slice is implemented

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when this slice is completed

## Status / Board Update

- keep this slice promoted on `_docs/_TASKS/README.md` while silhouette
  perception and typed action-hint planning remain open

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-128-02-01](./TASK-128-02-01_Perception_Boundary_And_Response_Contract_For_Silhouette_Analysis.md) | Define where silhouette analysis lives and how its outputs are exposed |
| 2 | [TASK-128-02-02](./TASK-128-02-02_Reference_And_Viewport_Mask_Extraction_Pipeline.md) | Define the deterministic mask-extraction/alignment path |
| 3 | [TASK-128-02-03](./TASK-128-02-03_Silhouette_Metrics_And_Typed_Action_Hint_Mapping.md) | Turn mask comparison into metric bundles and tool-oriented action hints |
| 4 | [TASK-128-02-04](./TASK-128-02-04_Iterate_Stage_Integration_Docs_And_Regression_Pack.md) | Adopt the new perception outputs into iterate-stage UX, docs, and regressions |
