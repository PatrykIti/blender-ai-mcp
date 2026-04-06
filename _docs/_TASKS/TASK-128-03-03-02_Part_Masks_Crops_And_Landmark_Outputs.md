# TASK-128-03-03-02: Part Masks, Crops, and Landmark Outputs

**Parent:** [TASK-128-03-03](./TASK-128-03-03_Part_Masks_Crops_Landmarks_And_Localized_Hints.md)
**Status:** ✅ Done
**Priority:** 🟠 High

## Objective

Define the concrete localized outputs the sidecar should produce for later
perception work.

## Repository Touchpoints

- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/vision/`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- planned outputs cover masks, crops, and landmarks clearly
- the output model can support part-specific comparisons later
- docs explain how these outputs complement global silhouette metrics

## Docs To Update

- `_docs/_VISION/README.md`

## Changelog Impact

- include in the parent slice changelog entry when shipped
