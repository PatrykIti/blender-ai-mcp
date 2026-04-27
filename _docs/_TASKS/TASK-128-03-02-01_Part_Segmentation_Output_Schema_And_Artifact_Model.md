# TASK-128-03-02-01: Part-Segmentation Output Schema and Artifact Model

**Parent:** [TASK-128-03-02](./TASK-128-03-02_Part_Segmentation_Contract_And_Provider_Interface.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Define the generic output model for part-aware results, including planned
artifacts such as:

- `part_masks`
- `part_crops`
- `landmarks`
- `part_proportions`

## Repository Touchpoints

- `server/adapters/mcp/contracts/reference.py`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- the output schema is product-facing and vendor-neutral
- artifact naming is explicit and reusable
- the schema complements earlier silhouette outputs instead of replacing them

## Docs To Update

- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- include in the parent slice changelog entry when shipped
