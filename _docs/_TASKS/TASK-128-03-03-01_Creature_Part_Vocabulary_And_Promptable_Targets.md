# TASK-128-03-03-01: Creature Part Vocabulary and Promptable Targets

**Parent:** [TASK-128-03-03](./TASK-128-03-03_Part_Masks_Crops_Landmarks_And_Localized_Hints.md)
**Status:** ✅ Done
**Priority:** 🟠 High

## Objective

Define the first reusable creature-part vocabulary for sidecar segmentation,
such as:

- `head`
- `ear`
- `snout`
- `eye`
- `torso`
- `tail`
- `paw`

## Repository Touchpoints

- `_docs/_VISION/README.md`
- `server/adapters/mcp/contracts/reference.py`

## Acceptance Criteria

- part names are generic and reusable across common creature builds
- the vocabulary fits staged front/side creature work
- later provider adapters can target the same vocabulary

## Docs To Update

- `_docs/_VISION/README.md`

## Changelog Impact

- include in the parent slice changelog entry when shipped
