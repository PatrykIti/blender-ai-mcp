# TASK-128-03-01-01: Sidecar Packaging and Dependency Isolation

**Parent:** [TASK-128-03-01](./TASK-128-03-01_Runtime_Boundary_Packaging_And_Opt_In_Policy.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Define how the part-segmentation sidecar is packaged so heavyweight runtime
dependencies stay outside the default server bootstrap path.

## Repository Touchpoints

- `server/infrastructure/config.py`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- the dependency-isolation plan is explicit
- default bootstrap remains lightweight when the sidecar is absent
- docs explain where the sidecar boundary begins and ends

## Docs To Update

- `_docs/_VISION/README.md`

## Changelog Impact

- include in the parent slice changelog entry when shipped
