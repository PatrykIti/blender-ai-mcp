# TASK-122-02-06: `macro_place_supported_pair`

**Parent:** [TASK-122-02](./TASK-122-02_Creature_Correction_Macro_Tool_Wave.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium

**Completion Summary:** Added `macro_place_supported_pair` as a bounded mirrored-pair placement macro against a shared support surface. The first MVP preserves one anchor object (`left`, `right`, or `auto`), keeps explicit mirror-plane and support-contact constraints separate, blocks when those constraints would require materially different support coordinates, and generalizes the public naming immediately so the tool fits non-body cases such as chair legs or landing skids.

## Objective

Add a bounded macro for placing or correcting one mirrored pair against a shared support surface without drifting into rigging or free-form posing.

## Repository Touchpoints

- `server/domain/tools/`
- `server/application/tool_handlers/`
- `server/adapters/mcp/areas/`
- `server/adapters/mcp/contracts/`
- `server/adapters/mcp/dispatcher.py`
- `server/adapters/mcp/transforms/`
- `server/router/infrastructure/tools_metadata/`
- `tests/unit/`
- `tests/e2e/`
- `README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/`

## Acceptance Criteria

- the macro can place or correct one mirrored pair against one explicit support object using bounded symmetry and support-contact rules
- the macro report records the placement/support actions taken and the follow-up checks needed to confirm symmetry and support contact

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_ROUTER/README.md` when router-aware metadata or guided usage changes
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/` for handler, MCP wrapper, structured delivery, provider inventory, and visibility coverage
- `tests/e2e/` for mirrored support placement and contact verification in Blender

## Changelog Impact

- add a `_docs/_CHANGELOG/*.md` entry when this leaf changes macro behavior, contracts, metadata, or public docs

## Status / Board Update

- this leaf is closed; the parent macro wave remains in progress for the remaining creature-correction macros
