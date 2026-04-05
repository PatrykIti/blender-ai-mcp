# TASK-128-02-03-01: Typed Action-Hint Schema and Vocabulary

**Parent:** [TASK-128-02-03](./TASK-128-02-03_Silhouette_Metrics_And_Typed_Action_Hint_Mapping.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Define the typed `action_hints` schema, including fields such as:

- `tool_name`
- `reason`
- `priority`
- `arguments_hint`
- `target_objects`
- `stage_fit`
- `confidence`

## Repository Touchpoints

- `server/adapters/mcp/contracts/reference.py`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- the schema is explicit and bounded
- field names are stable and product-facing
- docs explain how the hints complement existing correction outputs

## Docs To Update

- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- include in the parent slice changelog entry when shipped
