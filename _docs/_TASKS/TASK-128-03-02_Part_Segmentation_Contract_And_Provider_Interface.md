# TASK-128-03-02: Part-Segmentation Contract and Provider Interface

**Parent:** [TASK-128-03](./TASK-128-03_Optional_Part_Segmentation_Sidecar_And_Part_Aware_Perception.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Define one generic provider contract for part-aware segmentation outputs so
later model/runtime choices plug into the repo without changing the product
surface.

## Repository Touchpoints

- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/vision/`
- `server/adapters/mcp/areas/reference.py`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- the sidecar contract is vendor-neutral and product-facing
- later provider choices can fit behind the same bounded interface
- the contract keeps segmentation advisory rather than authoritative

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- include in the parent slice changelog entry when shipped

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-128-03-02-01](./TASK-128-03-02-01_Part_Segmentation_Output_Schema_And_Artifact_Model.md) | Define the output fields and artifact model for part-aware results |
| 2 | [TASK-128-03-02-02](./TASK-128-03-02-02_Generic_Sidecar_Provider_Boundary.md) | Define the provider boundary for SAM-class, grounded, or similar segmenters |
