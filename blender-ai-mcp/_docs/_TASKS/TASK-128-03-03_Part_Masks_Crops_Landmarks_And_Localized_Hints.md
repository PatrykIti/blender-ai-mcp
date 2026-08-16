# TASK-128-03-03: Part Masks, Crops, Landmarks, and Localized Hints

**Parent:** [TASK-128-03](./TASK-128-03_Optional_Part_Segmentation_Sidecar_And_Part_Aware_Perception.md)
**Status:** ✅ Done
**Priority:** 🟠 High

## Objective

Define the actual part-aware outputs and how they can later improve localized
creature guidance.

## Repository Touchpoints

- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/vision/`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- the repo has an explicit plan for part masks/crops/landmarks
- localized outputs are tied to creature-relevant part labels
- the later hint path remains compatible with Slice B silhouette/action-hint
  work

## Changelog Impact

- include in the parent slice changelog entry when shipped

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-128-03-03-01](./TASK-128-03-03-01_Creature_Part_Vocabulary_And_Promptable_Targets.md) | Define the first reusable part vocabulary for creature work |
| 2 | [TASK-128-03-03-02](./TASK-128-03-03-02_Part_Masks_Crops_And_Landmark_Outputs.md) | Define the localized outputs produced by the sidecar |
| 3 | [TASK-128-03-03-03](./TASK-128-03-03-03_Part_Aware_Hint_And_Metric_Consumption_Path.md) | Define how part-aware outputs feed later hints and metrics |
