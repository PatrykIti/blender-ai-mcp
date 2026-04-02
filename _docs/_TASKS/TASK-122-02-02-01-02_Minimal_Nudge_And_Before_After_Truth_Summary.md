# TASK-122-02-02-01-02: Minimal Nudge and Before/After Truth Summary

**Parent:** [TASK-122-02-02-01](./TASK-122-02-02-01_Repair_Macro_Contract_Inference_And_Candidate_Exposure.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

## Objective

Implement the bounded minimal-nudge repair itself and return before/after truth
summary instead of only a transform report.

## Repository Touchpoints

- `server/application/tool_handlers/`
- `server/adapters/mcp/contracts/`
- `server/adapters/mcp/areas/`
- `tests/unit/`
- `tests/e2e/`

## Acceptance Criteria

- the macro computes a bounded minimal nudge instead of a fresh re-placement
- the report includes before/after truth summary and verification hints

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Tests To Add/Update

- `tests/unit/` for repair math / bounded movement behavior
- `tests/e2e/` for real Blender pair-repair behavior

## Changelog Impact

- include this scope in the eventual repair-macro changelog entry when it ships

## Status / Board Update

- update this leaf and its parent when the bounded repair behavior is implemented
