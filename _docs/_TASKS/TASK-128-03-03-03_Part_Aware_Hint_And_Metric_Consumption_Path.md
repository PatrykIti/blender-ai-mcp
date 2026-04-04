# TASK-128-03-03-03: Part-Aware Hint and Metric Consumption Path

**Parent:** [TASK-128-03-03](./TASK-128-03-03_Part_Masks_Crops_Landmarks_And_Localized_Hints.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Define how part-aware outputs would later feed localized hints, crops, and
measurements without bypassing the existing perception/truth boundaries.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- the consumption path is explicit and boundary-safe
- part-aware outputs are additive to Slice B, not a replacement for it
- the repo has a clear plan for localized future hints

## Docs To Update

- `_docs/_VISION/README.md`

## Changelog Impact

- include in the parent slice changelog entry when shipped
