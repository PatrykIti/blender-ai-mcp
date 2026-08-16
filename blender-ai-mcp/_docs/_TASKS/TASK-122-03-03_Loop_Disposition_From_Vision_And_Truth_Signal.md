# TASK-122-03-03: Loop Disposition From Vision and Truth Signal

**Parent:** [TASK-122-03](./TASK-122-03_Hybrid_Vision_Truth_Correction_Loop.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** `reference_iterate_stage_checkpoint(...)` now computes `loop_disposition` from both actionable focus and deterministic truth evidence. The first bounded rule keeps the existing actionability + repeated-focus path, but additionally escalates to `inspect_validate` when the highest-priority ranked correction candidates contain high-priority truth evidence such as `contact_failure`, `overlap`, or `measurement_error`.

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

- this leaf is closed; the hybrid-loop parent remains in progress for real eval and prompting work
