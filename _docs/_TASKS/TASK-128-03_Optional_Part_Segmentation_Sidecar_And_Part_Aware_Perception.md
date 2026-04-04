# TASK-128-03: Optional Part-Segmentation Sidecar and Part-Aware Perception

**Parent:** [TASK-128](./TASK-128_Reference_Guided_Creature_Build_Surface_And_Perception_Reliability.md)
**Status:** ⏳ To Do
**Priority:** 🟡 Medium

## Objective

Define the optional sidecar path for part-aware reference perception so later
creature work can produce part masks, crops, and landmarks without turning a
heavy segmentation stack into the default repo runtime.

## Business Problem

Slice B solves the biggest current gap with deterministic silhouette metrics,
but silhouette alone still has limits:

- it is strong on global shape
- it is weaker on localized part crops and part-specific masks
- it does not inherently localize `ear`, `snout`, `tail`, or `paw` regions

An optional sidecar can help later by producing part-aware outputs for:

- better localized corrective hints
- part-specific crop review
- reusable per-part proportions/landmarks

But that work must stay bounded:

- no mandatory heavy GPU dependency in the default server path
- no confusion between segmentation output and scene truth
- no router-policy takeover by a model-specific sidecar

## Business Outcome

If this slice is done correctly:

- the repo gets one explicit optional path for part-aware perception
- the sidecar contract is reusable across vendors/models
- later model choices such as SAM-class or grounded segmenters can plug in
  behind one bounded interface
- operators can opt into the heavier path only when the added value justifies
  the runtime cost

## Scope

This slice covers:

- runtime/dependency isolation and opt-in execution policy
- generic sidecar/provider contract for part segmentation
- planned part-mask / crop / landmark outputs
- evaluation and adoption guidance for part-aware perception

This slice does **not** cover:

- making segmentation mandatory for normal guided sessions
- full 3D reconstruction pipelines
- changing the truth-layer ownership model

## Acceptance Criteria

- the repo has one explicit optional sidecar strategy for part-aware
  segmentation
- runtime/dependency policy keeps the default MCP server lightweight
- outputs are defined in generic product terms rather than one vendor-specific
  schema
- docs and evaluation notes explain when this sidecar is worth enabling and
  when silhouette-only guidance is enough

## Repository Touchpoints

- `server/infrastructure/config.py`
- `server/adapters/mcp/vision/`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/areas/reference.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_vision_*`
- `_docs/_VISION/README.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `_docs/_TESTS/README.md`

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `_docs/_TESTS/README.md`

## Tests To Add/Update

- focused `tests/unit/adapters/mcp/test_vision_*` coverage
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/vision/` for any real sidecar adoption

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when this slice is completed

## Status / Board Update

- keep this slice promoted on `_docs/_TASKS/README.md` as an optional
  follow-on after Slice B

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-128-03-01](./TASK-128-03-01_Runtime_Boundary_Packaging_And_Opt_In_Policy.md) | Keep the sidecar optional, isolated, and failure-tolerant |
| 2 | [TASK-128-03-02](./TASK-128-03-02_Part_Segmentation_Contract_And_Provider_Interface.md) | Define one vendor-neutral contract for part-aware outputs |
| 3 | [TASK-128-03-03](./TASK-128-03-03_Part_Masks_Crops_Landmarks_And_Localized_Hints.md) | Define the actual part-aware outputs and how they feed later hints |
| 4 | [TASK-128-03-04](./TASK-128-03-04_Evaluation_Adoption_Guidance_And_Regression_Plan.md) | Add cost/latency gates, operator guidance, and test planning |
