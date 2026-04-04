# TASK-128-02-02-01: Reference Mask Extraction and Normalization

**Parent:** [TASK-128-02-02](./TASK-128-02-02_Reference_And_Viewport_Mask_Extraction_Pipeline.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Define how reference images are converted into stable silhouette masks and
normalized for front/side creature comparison.

## Repository Touchpoints

- `server/adapters/mcp/vision/evaluation.py`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- the repo has a documented path for reference-mask extraction
- normalization assumptions are explicit
- the path stays independent from heavyweight segmentation sidecars

## Docs To Update

- `_docs/_VISION/README.md`

## Changelog Impact

- include in the parent slice changelog entry when shipped
