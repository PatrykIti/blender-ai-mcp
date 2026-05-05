# TASK-161-02: Addon Proof-Lane And Owner Doc Alignment After TASK-159

**Parent:** [TASK-161](./TASK-161_TASK-159_Closeout_Seam_And_Proof_Lane_Alignment.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Align addon owner docs and proof lanes with the live post-`TASK-159`
mixins/structural-read runtime so the closeout evidence matches what Blender now
returns and registers.

## Repository Touchpoints

- `_docs/_ADDON/README.md`
- `blender_addon/application/handlers/scene.py`
- `blender_addon/application/handlers/scene_structural_read_mixin.py`
- `tests/unit/addon/test_addon_registration.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/scene/test_scene_state_assistants.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/e2e/tools/scene/test_scene_read_runtime_surfaces.py`
- `tests/e2e/tools/scene/test_scene_inspect_runtime_surfaces.py`

## Implementation Notes

- keep runtime behavior stable; this follow-on is about proof/docs alignment
- update stale fixture payloads to the live `root_count` / `hierarchy` and
  `bbox_center` / `offset_from_center` / `estimated_type` shapes
- strengthen registration coverage so the mixin-based `SceneHandler` still maps
  to the registered scene RPC surface

## Tests To Add/Update

- `tests/unit/addon/test_addon_registration.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/scene/test_scene_state_assistants.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/addon/test_addon_registration.py tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/tools/scene/test_scene_contracts.py tests/unit/tools/scene/test_scene_state_assistants.py tests/unit/adapters/mcp/test_structured_contract_delivery.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/tools/scene/test_scene_read_runtime_surfaces.py tests/e2e/tools/scene/test_scene_inspect_runtime_surfaces.py -q`

## Docs To Update

- `_docs/_ADDON/README.md`

## Changelog Impact

- include in the parent `TASK-161` changelog entry when shipped

## Acceptance Criteria

- addon owner docs describe the mixin-based `SceneHandler` truthfully
- structural-read/origin fixtures match the live post-split payloads
- registration proof is strong enough that missing scene mixin wiring would no
  longer pass silently

## Status / Board Update

- completed as a historical child of `TASK-161`
- no separate promoted board row is needed for this slice

## Completion Summary

Completed on 2026-05-05.

- aligned addon owner docs with the live mixin-based `SceneHandler`
- refreshed structural-read and origin proof lanes to the current payload shapes
- strengthened addon registration coverage for the post-split scene RPC surface
