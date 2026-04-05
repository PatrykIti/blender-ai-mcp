# TASK-122-01-02: Contact, Gap, Alignment, and Overlap Correction Bundle

**Parent:** [TASK-122-01](./TASK-122-01_Spatial_Correction_Truth_Bundles_For_Assembled_Models.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** Added a correction-oriented `truth_bundle` for stage compare and iterate flows. The bundle now groups contact, gap, alignment, and overlap findings per assembled-target pair, summarizes pairing strategy and failure counts, and is passed both in the reference response contract and into the vision request as deterministic truth context.

## Objective

Build one correction-ready truth bundle that combines contact, gap, alignment, and overlap findings for assembled targets instead of returning isolated tool-local facts.

## Repository Touchpoints

- `server/adapters/mcp/contracts/scene.py`
- `server/adapters/mcp/areas/scene.py`
- `server/application/tool_handlers/scene_handler.py`
- `server/router/application/`
- `tests/unit/tools/scene/`
- `tests/unit/router/`
- `tests/e2e/tools/scene/`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`

## Acceptance Criteria

- one structured bundle reports the relevant contact/gap/alignment/overlap findings for the assembled target scope
- the bundle includes deterministic findings and actionable deltas that the correction loop can consume directly

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md` if the truth-bundle surface changes

## Tests To Add/Update

- `tests/unit/tools/scene/`
- `tests/unit/router/`
- `tests/e2e/tools/scene/` when the shipped behavior depends on real Blender geometry

## Changelog Impact

- add a `_docs/_CHANGELOG/*.md` entry when this leaf changes truth-bundle contracts, loop handoff behavior, or public docs

## Status / Board Update

- this leaf is closed; the parent task summary and `_docs/_TASKS/README.md` now reflect that `TASK-122` work is actively in progress
