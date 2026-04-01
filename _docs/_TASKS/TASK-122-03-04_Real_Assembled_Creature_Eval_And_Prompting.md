# TASK-122-03-04: Real Assembled Creature Eval and Prompting

**Parent:** [TASK-122-03](./TASK-122-03_Hybrid_Vision_Truth_Correction_Loop.md)  
**Status:** ⏳ To Do  
**Priority:** 🟡 Medium

## Objective

Validate the hybrid correction loop on real assembled-creature scenarios, prompts, and regression packs.

## Repository Touchpoints

- `server/adapters/mcp/vision/`
- `server/adapters/mcp/contracts/`
- `server/application/tool_handlers/router_handler.py`
- `server/router/application/`
- `tests/unit/adapters/mcp/`
- `tests/unit/router/`
- `tests/e2e/vision/`
- `tests/e2e/router/`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`

## Acceptance Criteria

- real assembled-creature scenarios exist to validate the hybrid loop against practical failure modes
- prompting and evaluation guidance are explicit enough that later loop regressions can be measured repeatably

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `_docs/_ROUTER/README.md` when loop policy or handoff semantics change

## Tests To Add/Update

- `tests/unit/adapters/mcp/`
- `tests/unit/router/`
- `tests/e2e/vision/`
- `tests/e2e/router/`

## Changelog Impact

- add a `_docs/_CHANGELOG/*.md` entry when this leaf changes hybrid-loop contracts, disposition policy, or follow-up behavior

## Status / Board Update

- update this leaf, its parent task, and `_docs/_TASKS/README.md` when the hybrid-loop work advances or closes
