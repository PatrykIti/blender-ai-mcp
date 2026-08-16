# TASK-154-03-02: Prompt Operator And Historical Closeout For Guided Naming

**Parent:** [TASK-154-03](./TASK-154-03_Regression_And_Docs_Closeout_For_Guided_Naming_Policy.md)
**Depends On:** [TASK-154-03-01](./TASK-154-03-01_Unit_And_Transport_Regression_Matrix_For_Guided_Naming_Policy.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Align prompts, operator docs, changelog history, and board/task state with the
final guided naming-policy behavior.

## Repository Touchpoints

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_CHANGELOG/README.md`
- `_docs/_TASKS/README.md`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Detailed Implementation Notes

- docs should state clearly:
  - preferred semantic naming remains the default guidance
  - the server can now warn or block on opaque role-sensitive names
  - `guided_register_part(...)` remains canonical
  - `guided_role=...` remains convenience-only
- changelog and board updates should ship in the same branch as the runtime
  behavior

## Acceptance Criteria

- docs and docs-parity tests describe the same shipped naming policy
- changelog and board state are updated when TASK-154 closes

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_CHANGELOG/README.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Changelog Impact

- add the parent TASK-154 historical entry here

## Completion Summary

- updated prompt/operator docs, changelog history, and task board state to
  match the shipped naming-policy behavior
