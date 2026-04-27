# TASK-128-02-02-02: Viewport Mask Capture and Alignment

**Parent:** [TASK-128-02-02](./TASK-128-02-02_Reference_And_Viewport_Mask_Extraction_Pipeline.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Define how stage checkpoint captures are turned into aligned silhouette masks
without breaking the current deterministic capture-bundle contract.

## Repository Touchpoints

- `server/adapters/mcp/vision/capture.py`
- `server/adapters/mcp/areas/reference.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Acceptance Criteria

- viewport mask generation fits the current stage-capture model
- alignment rules are explicit for target/front/side/full-scope comparisons
- tests can later validate the alignment assumptions deterministically

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped
