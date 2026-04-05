# TASK-128-02-01-02: Silhouette Output Schema and Response Placement

**Parent:** [TASK-128-02-01](./TASK-128-02-01_Perception_Boundary_And_Response_Contract_For_Silhouette_Analysis.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Define the response shape for silhouette-analysis outputs, including the future
typed `action_hints` placement in compare/iterate-stage contracts.

## Repository Touchpoints

- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/areas/reference.py`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- the schema covers silhouette metrics and typed action hints explicitly
- compare/iterate response placement is consistent and bounded
- docs explain how the new fields relate to existing correction outputs

## Docs To Update

- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- include in the parent slice changelog entry when shipped
