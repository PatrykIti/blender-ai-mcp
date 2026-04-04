# TASK-128-02-01: Perception Boundary and Response Contract for Silhouette Analysis

**Parent:** [TASK-128-02](./TASK-128-02_Deterministic_Silhouette_Analysis_And_Typed_Action_Hints.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Define one explicit contract for silhouette/perception outputs and place it in
the existing vision/reference layer without leaking image analysis into the
router or truth layers.

## Repository Touchpoints

- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/vision/`
- `_docs/_VISION/README.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`

## Acceptance Criteria

- the repo defines where silhouette-analysis outputs live in the public
  response model
- boundary docs make it explicit that silhouette metrics are perception, not
  truth
- the contract is stable enough for later part-segmentation work to reuse

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`

## Changelog Impact

- include in the parent slice changelog entry when shipped

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-128-02-01-01](./TASK-128-02-01-01_Perception_Layer_Ownership_And_Boundary_Rules.md) | Write the ownership rules for silhouette analysis vs truth/router |
| 2 | [TASK-128-02-01-02](./TASK-128-02-01-02_Silhouette_Output_Schema_And_Response_Placement.md) | Define the new response fields and where they belong |
