# TASK-122-02-02-01-01: Truth-Driven Pair Input and Side Preservation

**Parent:** [TASK-122-02-02-01](./TASK-122-02-02-01_Repair_Macro_Contract_Inference_And_Candidate_Exposure.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** The repair macro input model now distinguishes repair from fresh placement. `macro_align_part_with_contact` accepts pair-oriented repair inputs, optional `normal_axis`, `preserve_side`, and a bounded `max_nudge`, and preserves the current side by default when that side is clear.

## Objective

Define the repair input model for one already-related pair and make current
side preservation explicit by default.

## Repository Touchpoints

- `server/application/tool_handlers/`
- `server/adapters/mcp/contracts/`
- `server/adapters/mcp/areas/`
- `tests/unit/`

## Acceptance Criteria

- the repair input model distinguishes fresh placement from repair intent
- current side preservation is explicit and bounded instead of heuristic-only

## Docs To Update

- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/` for input validation and side-preservation behavior

## Changelog Impact

- include this scope in the eventual repair-macro changelog entry when it ships

## Status / Board Update

- this leaf is closed
