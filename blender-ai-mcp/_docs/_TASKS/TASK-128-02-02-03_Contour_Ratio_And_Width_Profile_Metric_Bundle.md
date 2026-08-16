# TASK-128-02-02-03: Contour, Ratio, and Width-Profile Metric Bundle

**Parent:** [TASK-128-02-02](./TASK-128-02-02_Reference_And_Viewport_Mask_Extraction_Pipeline.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Define the first deterministic metric bundle derived from silhouette masks.

## Technical Direction

Target initial metrics:

- silhouette overlap / contour drift
- width profile by normalized height bands
- head/body ratio
- ear height and ear base width
- snout length and snout drop
- tail arc height
- paw placement bands

## Repository Touchpoints

- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/areas/reference.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- the metric bundle is explicit and generic enough for creature blockout use
- metrics are structured, not prose-only
- the bundle is designed for regression-friendly deterministic comparison

## Docs To Update

- `_docs/_VISION/README.md`

## Changelog Impact

- include in the parent slice changelog entry when shipped
