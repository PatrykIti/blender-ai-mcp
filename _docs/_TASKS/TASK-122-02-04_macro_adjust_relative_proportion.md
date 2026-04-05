# TASK-122-02-04: `macro_adjust_relative_proportion`

**Parent:** [TASK-122-02](./TASK-122-02_Creature_Correction_Macro_Tool_Wave.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** Added `macro_adjust_relative_proportion` as a bounded proportion-repair macro. The first MVP reads the current cross-object ratio through `scene_assert_proportion`, scales one explicit target (`primary` or `reference`) within `max_scale_delta`, and re-checks the result instead of relying on ad hoc scale guessing or open-ended sculpting. The public naming was generalized immediately so the tool can serve non-creature use cases just as naturally as creature modeling.

## Objective

Add a bounded macro for correcting large cross-object ratio drift through a bounded scale adjustment.

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

- the macro can adjust cross-object proportion using bounded scale or transform rules instead of open-ended sculpting
- the macro report makes the proportion target and the recommended truth checks explicit

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

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-122-02-04-01](./TASK-122-02-04-01_Public_Naming_Generalization_For_Ratio_Repair.md) | Generalize the public naming and parameter model so the tool is not creature-specific |
