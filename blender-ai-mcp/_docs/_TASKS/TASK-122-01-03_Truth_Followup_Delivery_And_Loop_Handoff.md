# TASK-122-01-03: Truth Follow-Up Delivery and Loop Handoff

**Parent:** [TASK-122-01](./TASK-122-01_Spatial_Correction_Truth_Bundles_For_Assembled_Models.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** Added a loop-ready `truth_followup` payload on top of the new `truth_bundle`. Stage compare and iterate responses now expose focus pairs, actionable truth findings, and recommended deterministic re-check tools so later loop logic can consume a structured handoff instead of raw measure/assert payloads.

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

- this leaf is closed; the parent truth-bundle task is now complete and the `TASK-122` umbrella remains in progress for the remaining macro and hybrid-loop work
