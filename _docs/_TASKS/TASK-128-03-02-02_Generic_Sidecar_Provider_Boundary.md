# TASK-128-03-02-02: Generic Sidecar Provider Boundary

**Parent:** [TASK-128-03-02](./TASK-128-03-02_Part_Segmentation_Contract_And_Provider_Interface.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Define the provider boundary so SAM-class, grounded segmenters, or future
alternatives can all fit behind one bounded interface.

## Repository Touchpoints

- `server/adapters/mcp/vision/`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- the provider interface is generic enough for multiple segmentation families
- no one vendor/model becomes the public product contract
- the boundary remains compatible with the repo's optional-runtime strategy

## Docs To Update

- `_docs/_VISION/README.md`

## Changelog Impact

- include in the parent slice changelog entry when shipped
