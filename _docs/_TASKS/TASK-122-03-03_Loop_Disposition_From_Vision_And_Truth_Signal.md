# TASK-122-03-03: Loop Disposition From Vision and Truth Signal

**Parent:** [TASK-122-03](./TASK-122-03_Hybrid_Vision_Truth_Correction_Loop.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

## Objective

Recompute `loop_disposition` from both visual and geometric evidence instead of relying on vision-only continuation semantics.

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

- loop disposition can respond to both visual mismatch and deterministic spatial failure signals
- the disposition rules remain bounded and explainable instead of collapsing into open-ended model judgment

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
