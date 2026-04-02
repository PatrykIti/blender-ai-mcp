# TASK-122-02-07: `macro_cleanup_part_intersections`

**Parent:** [TASK-122-02](./TASK-122-02_Creature_Correction_Macro_Tool_Wave.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** Added `macro_cleanup_part_intersections` as a bounded pair-overlap cleanup macro. The first MVP reads overlap truth before moving anything, infers a stable cleanup axis from the current overlap footprint, preserves the current side when possible, pushes the moving object out to contact or a small gap, and blocks when the required cleanup push exceeds `max_push`. `truth_followup` now also surfaces this macro as a candidate for overlap-driven pair issues.

## Objective

Add a bounded macro for resolving or reducing obvious pairwise intersections without drifting into free-form collision solving.

## Repository Touchpoints

- `server/domain/tools/`
- `server/application/tool_handlers/`
- `server/adapters/mcp/areas/`
- `server/adapters/mcp/contracts/`
- `server/adapters/mcp/dispatcher.py`
- `server/adapters/mcp/transforms/`
- `server/adapters/mcp/areas/reference.py`
- `server/router/infrastructure/tools_metadata/`
- `tests/unit/`
- `tests/e2e/`
- `README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/`

## Acceptance Criteria

- the macro can reduce or resolve obvious pairwise intersections with bounded correction rules rather than unconstrained cleanup
- the macro report states which overlap was targeted and which deterministic overlap/contact checks should run next

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_ROUTER/README.md` when router-aware metadata or guided usage changes
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/` for handler, MCP wrapper, structured delivery, metadata alignment, truth-followup, and surface coverage
- `tests/e2e/` for overlap cleanup against real scene geometry in Blender

## Changelog Impact

- add a `_docs/_CHANGELOG/*.md` entry when this leaf changes macro behavior, contracts, metadata, or public docs

## Status / Board Update

- this leaf is closed; the parent macro wave is now complete
