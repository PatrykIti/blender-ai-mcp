# TASK-128-02-02: Reference and Viewport Mask Extraction Pipeline

**Parent:** [TASK-128-02](./TASK-128-02_Deterministic_Silhouette_Analysis_And_Typed_Action_Hints.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Plan the deterministic pipeline that extracts and aligns silhouette masks from
reference images and stage viewport captures.

## Repository Touchpoints

- `server/adapters/mcp/vision/capture.py`
- `server/adapters/mcp/vision/capture_runtime.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/areas/reference.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_vision_capture_runtime.py`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- the mask-extraction path is explicit for both references and viewport
  captures
- alignment assumptions across front/side/full-silhouette scopes are defined
- the plan is deterministic enough to support repeatable regression tests

## Changelog Impact

- include in the parent slice changelog entry when shipped

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-128-02-02-01](./TASK-128-02-02-01_Reference_Mask_Extraction_And_Normalization.md) | Define how reference images become clean silhouette masks |
| 2 | [TASK-128-02-02-02](./TASK-128-02-02-02_Viewport_Mask_Capture_And_Alignment.md) | Define how captured stage images become aligned silhouette masks |
| 3 | [TASK-128-02-02-03](./TASK-128-02-02-03_Contour_Ratio_And_Width_Profile_Metric_Bundle.md) | Define the first deterministic metric bundle derived from those masks |
