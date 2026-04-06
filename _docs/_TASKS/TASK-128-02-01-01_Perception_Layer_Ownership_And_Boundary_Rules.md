# TASK-128-02-01-01: Perception Layer Ownership and Boundary Rules

**Parent:** [TASK-128-02-01](./TASK-128-02-01_Perception_Boundary_And_Response_Contract_For_Silhouette_Analysis.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Record the boundary rules that keep silhouette analysis inside the
vision/reference perception layer and out of router policy and truth authority.

## Repository Touchpoints

- `_docs/_VISION/README.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- boundary docs clearly separate perception, truth, and policy
- silhouette metrics are described as advisory but structured
- boundary docs explicitly treat `vision_contract_profile` as external
  prompt/schema/parser routing only, not as scene-truth or silhouette-ownership
  authority
- later slices can reuse the same ownership model

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`

## Changelog Impact

- include in the parent slice changelog entry when shipped
