# TASK-128-02-03: Silhouette Metrics and Typed Action-Hint Mapping

**Parent:** [TASK-128-02](./TASK-128-02_Deterministic_Silhouette_Analysis_And_Typed_Action_Hints.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Map silhouette-analysis findings into typed `action_hints` that suggest
candidate tools and bounded argument hints without pretending to be the truth
layer.

## Repository Touchpoints

- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/vision/reporting.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- the repo defines one explicit typed action-hint schema
- silhouette findings can map to bounded candidate tools and argument hints
- the mapping stays deterministic and explainable

## Docs To Update

- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-128-02-03-01](./TASK-128-02-03-01_Typed_Action_Hint_Schema_And_Vocabulary.md) | Define the action-hint response model and vocabulary |
| 2 | [TASK-128-02-03-02](./TASK-128-02-03-02_Silhouette_Finding_To_Tool_Mapping_Rules.md) | Define how metric findings map to bounded tool suggestions |
