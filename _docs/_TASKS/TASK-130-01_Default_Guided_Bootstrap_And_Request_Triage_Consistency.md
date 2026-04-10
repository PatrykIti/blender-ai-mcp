# TASK-130-01: Default Guided Bootstrap And Request Triage Consistency

**Parent:** [TASK-130](./TASK-130_Default_Guided_Surface_Bootstrap_Consistency.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Make the production default guided story and the first-step request triage
contract explicit, so the model starts in the right operating mode and does
not waste time on mismatched bootstrap assumptions.

## Repository Touchpoints

- `server/infrastructure/config.py`
- `server/adapters/mcp/surfaces.py`
- `server/adapters/mcp/areas/router.py`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Acceptance Criteria

- one explicit production bootstrap/default story is chosen and reflected in
  runtime + docs
- first-step request triage is documented and testable:
  - build/workflow goal
  - utility/capture/scene-prep
  - guided manual build continuation
- the server/docs/examples do not imply conflicting bootstrap assumptions

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-130-01-01](./TASK-130-01-01_Align_Runtime_Default_Client_Examples_And_Operator_Story.md) | Align runtime defaults, client examples, and operator docs around one guided production story |
| 2 | [TASK-130-01-02](./TASK-130-01-02_Explicit_First_Step_Request_Triage_And_Recovery_Path.md) | Make the first-step request classification and recovery path explicit for the guided surface |

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- focused bootstrap/triage tests under `tests/unit/adapters/mcp/`

## Changelog Impact

- include in the parent TASK-130 changelog entry
