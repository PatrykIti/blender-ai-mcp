# TASK-122-02-05: `macro_adjust_tail_arc`

**Parent:** [TASK-122-02](./TASK-122-02_Creature_Correction_Macro_Tool_Wave.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium

**Completion Summary:** Added `macro_adjust_tail_arc` as a bounded chain macro for segmented tails. The first MVP takes an ordered list of existing tail segment objects, keeps the first segment anchored, and places the remaining segments along a planar arc with deterministic spacing and optional progressive rotation around one explicit rotation axis.

## Objective

Add a bounded macro for correcting segmented tail shape, arc, and placement without resorting to free-form tool chaining.

## Repository Touchpoints

- `server/domain/tools/`
- `server/application/tool_handlers/`
- `blender_addon/application/handlers/`
- `blender_addon/__init__.py`
- `server/adapters/mcp/areas/`
- `server/adapters/mcp/dispatcher.py`
- `server/infrastructure/di.py`
- `server/router/infrastructure/tools_metadata/`
- `tests/unit/`
- `tests/e2e/`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_ADDON/README.md`

## Acceptance Criteria

- the macro can adjust tail arc/placement through bounded parameters that stay compatible with assembled-model correction loops
- the macro report records what tail-shape correction was applied and which truth checks should validate the result

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_ADDON/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_ROUTER/README.md` when router-aware metadata or guided usage changes

## Tests To Add/Update

- `tests/unit/` for contract and handler coverage
- `tests/e2e/` when geometry, alignment, contact, or cleanup behavior changes in Blender

## Changelog Impact

- add a `_docs/_CHANGELOG/*.md` entry when this leaf changes macro behavior, contracts, metadata, or public docs

## Status / Board Update

- this leaf is closed; the parent macro wave remains in progress for the remaining creature-correction macros
