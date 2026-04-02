# TASK-122-02-03: `macro_place_symmetry_pair`

**Parent:** [TASK-122-02](./TASK-122-02_Creature_Correction_Macro_Tool_Wave.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** Added `macro_place_symmetry_pair` as a bounded pair-level symmetry macro. The first MVP preserves one anchor object (`left`, `right`, or `auto`), mirrors the follower object's center across an explicit mirror plane, and verifies the result with `scene_assert_symmetry` instead of relying on ad hoc mirrored transforms.

## Objective

Add a bounded macro for placing or correcting mirrored part pairs such as ears, eyes, or simple limbs.

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

- the macro can place or correct one mirrored pair using explicit axis/mirror rules instead of ad hoc transforms
- the macro report records the mirrored targets and the deterministic checks needed to validate symmetry/contact

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
