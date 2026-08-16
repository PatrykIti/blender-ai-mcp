# TASK-130-03-02: Prompt Operator And Historical Closeout For Generic Guided Governor

**Parent:** [TASK-130-03](./TASK-130-03_Regression_And_Docs_Closeout_For_Generic_Guided_Governor.md)
**Depends On:** [TASK-130-03-01](./TASK-130-03-01_Unit_And_Transport_Regression_Matrix_For_Generic_Guided_Governor.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Align prompt assets, operator docs, changelog history, and board/task state
with the final generic guided governor behavior.

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

## Acceptance Criteria

- docs and docs-parity tests describe the shipped generic-governor posture
- changelog and board state are updated when TASK-130 closes

## Changelog Impact

- add the parent TASK-130 historical entry here

## Completion Summary

- updated prompt/operator docs and historical tracking to match the shipped
  guided governor behavior
