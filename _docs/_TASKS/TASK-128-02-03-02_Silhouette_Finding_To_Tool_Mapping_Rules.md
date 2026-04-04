# TASK-128-02-03-02: Silhouette Finding to Tool-Mapping Rules

**Parent:** [TASK-128-02-03](./TASK-128-02-03_Silhouette_Metrics_And_Typed_Action_Hint_Mapping.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Define deterministic rules that turn silhouette findings into bounded candidate
tools and argument-hint shapes.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/vision/reporting.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Acceptance Criteria

- mappings are deterministic and explainable
- candidate tools stay within the intended creature build surface
- tests can later verify the mapping from representative silhouette findings

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped
