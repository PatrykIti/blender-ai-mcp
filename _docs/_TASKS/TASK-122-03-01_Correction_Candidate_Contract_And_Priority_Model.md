# TASK-122-03-01: Correction Candidate Contract and Priority Model

**Parent:** [TASK-122-03](./TASK-122-03_Hybrid_Vision_Truth_Correction_Loop.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** Added a merged `correction_candidates` contract for stage compare / iterate responses. The first MVP preserves source boundaries by nesting vision evidence, truth evidence, and bounded macro options inside one explicitly ranked candidate list. Truth-driven pair issues can now become `truth_only` or `hybrid` candidates, while unmatched vision focus items remain `vision_only` candidates instead of being flattened into ad hoc prose order.

## Objective

Define one merged contract that can carry vision mismatch signals, truth/spatial failure signals, macro-candidate fixes, and ordered correction priority.

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

- one merged correction-candidate contract can represent vision evidence, truth evidence, and macro candidates without losing source boundaries
- priority ordering is explicit enough that loop disposition and macro handoff do not depend on ad hoc prose ranking

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

- this leaf is closed; the hybrid-loop parent remains in progress for truth integration, disposition policy, and eval work
