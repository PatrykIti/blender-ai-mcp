# TASK-122-01-03: Truth Follow-Up Delivery and Loop Handoff

**Parent:** [TASK-122-01](./TASK-122-01_Spatial_Correction_Truth_Bundles_For_Assembled_Models.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

## Objective

Expose truth-bundle findings as loop-ready follow-up payloads instead of isolated raw tool responses.

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

- truth findings can be handed into the correction loop without ad hoc result rewriting
- the follow-up payload distinguishes inspect-only outcomes from macro-candidate-ready correction outcomes

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

- update this leaf, its parent task, and `_docs/_TASKS/README.md` when the work starts or closes
