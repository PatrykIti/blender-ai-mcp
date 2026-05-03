# TASK-159-01: Reference Area Modularization And Checkpoint Assembly Boundaries

**Parent:** [TASK-159](./TASK-159_Modularize_Oversized_Guided_Runtime_And_Scene_Owner_Files.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Split `server/adapters/mcp/areas/reference.py` into smaller ownership slices for:

- `planner_*`
- `truth_*`
- `silhouette_*`
- `view_diagnostics_*`
- `checkpoint_*`

while keeping the current public `reference_*` MCP tool surface and staged
response contracts stable.

## Business Problem

`reference.py` is now both the staged public surface and the home for too much
private policy/assembly logic:

- checkpoint capture orchestration
- truth-bundle shaping
- correction-candidate assembly
- planner summary / detail / handoff shaping
- silhouette analysis helpers
- view-diagnostics hint shaping
- reference image lifecycle helpers

That makes future work riskier than it needs to be:

- small planner changes touch vision and checkpoint code
- truth changes touch compare/iterate orchestration directly
- review scope for one bugfix becomes too broad
- the staged reference loop becomes the permanent dumping ground for every new
  helper instead of a bounded assembler

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- likely new sibling modules under `server/adapters/mcp/areas/` such as:
  - `reference_checkpoint.py`
  - `reference_truth.py`
  - `reference_planner.py`
  - `reference_silhouette.py`
  - `reference_view_diagnostics.py`
- `server/application/services/` when a helper can be made framework-free
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/adapters/mcp/providers/core_tools.py`
- `server/adapters/mcp/platform/capability_manifest.py`
- `server/adapters/mcp/vision/`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`
- `tests/unit/adapters/mcp/test_surface_manifest.py`
- `tests/e2e/tools/scene/test_scene_get_viewport.py`
- `tests/e2e/tools/scene/test_scene_get_viewport_camera.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `tests/e2e/vision/test_reference_stage_silhouette_contract.py`
- `tests/e2e/vision/test_goal_derived_gate_support_symmetry_surfaces.py`
- `tests/e2e/vision/test_reference_understanding_runtime_surface.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`

## Implementation Notes

- Keep `reference.py` as the public MCP facade and staged response assembler.
- Move private helper clusters by concern, not one function at a time.
- If a helper does not need `Context`, MCP contracts, or adapter-only imports,
  evaluate promoting it into `server/application/services/`.
- Keep compare / iterate response assembly in one visible place so future
  implementers can still trace the response contract end to end.
- Keep `REFERENCE_PUBLIC_TOOL_NAMES`, `register_reference_tools(...)`, and the
  provider/manifest import seam stable while helpers move behind the facade.
- Do not widen staged payloads during the extraction. This task is about module
  boundaries, not feature growth.
- Do not leave `reference_compare_current_view(...)` as an implicit remainder
  under the checkpoint or image-lifecycle leaves. Track its viewport-backed
  compare orchestration explicitly.
- Preserve current public tool names:
  - `reference_images`
  - `reference_compare_checkpoint`
  - `reference_compare_current_view`
  - `reference_compare_stage_checkpoint`
  - `reference_iterate_stage_checkpoint`

## Pseudocode

```python
# reference.py stays public facade
from server.adapters.mcp.areas.reference_checkpoint import build_stage_compare_result
from server.adapters.mcp.areas.reference_truth import build_truth_bundle
from server.adapters.mcp.areas.reference_planner import build_planner_outputs
from server.adapters.mcp.areas.reference_silhouette import build_silhouette_outputs
from server.adapters.mcp.areas.reference_view_diagnostics import build_view_hints

async def reference_compare_stage_checkpoint(...):
    checkpoint = build_stage_compare_result(...)
    truth = build_truth_bundle(...)
    planner = build_planner_outputs(...)
    silhouette = build_silhouette_outputs(...)
    view_hints = build_view_hints(...)
    return assemble_public_contract(...)
```

## Runtime / Security Contract Notes

- Keep current reference/vision authority boundaries intact:
  - vision/perception remains advisory
  - truth bundle remains authoritative for deterministic checks
- Preserve the current registration/discovery contract for the reference family:
  tool-name inventory, manifest exposure, and provider wiring are part of the
  public surface even when payloads stay unchanged.
- Do not leak provider keys, local paths, or oversized debug payloads while
  moving helpers.
- Preserve current budget-control behavior and trim semantics.

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-159-01-01](./TASK-159-01-01_Reference_Public_Facade_Registration_And_Checkpoint_Orchestrator_Split.md) | Stabilize the public facade, registration seam, and checkpoint orchestration before deeper helper extraction |
| 2 | [TASK-159-01-02](./TASK-159-01-02_Reference_Truth_Planner_And_Service_Promotion_Split.md) | Extract truth/planner helper clusters and identify framework-free logic that should move into application services |
| 3 | [TASK-159-01-03](./TASK-159-01-03_Reference_Silhouette_View_Diagnostics_And_Understanding_Sidecars.md) | Separate silhouette, view-diagnostics, and reference-understanding sidecars without changing advisory-vs-truth boundaries |
| 4 | [TASK-159-01-04](./TASK-159-01-04_Reference_Image_Lifecycle_And_Staged_Session_Integration.md) | Isolate reference image lifecycle and staged session integration helpers while preserving session/update semantics |
| 5 | [TASK-159-01-05](./TASK-159-01-05_Reference_Current_View_Capture_And_Compare_Orchestration.md) | Separate the live current-view capture/compare orchestration so the viewport-backed public compare path is not left implicit under the checkpoint leaves |

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`
- `tests/unit/adapters/mcp/test_surface_manifest.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `tests/e2e/vision/test_reference_stage_silhouette_contract.py`
- `tests/e2e/vision/test_goal_derived_gate_support_symmetry_surfaces.py`
- `tests/e2e/vision/test_reference_understanding_runtime_surface.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/adapters/mcp/test_provider_inventory.py tests/unit/adapters/mcp/test_tool_inventory.py tests/unit/adapters/mcp/test_surface_manifest.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/tools/scene/test_scene_get_viewport.py tests/e2e/tools/scene/test_scene_get_viewport_camera.py tests/e2e/vision/test_reference_stage_truth_handoff.py tests/e2e/vision/test_reference_stage_silhouette_contract.py tests/e2e/vision/test_goal_derived_gate_support_symmetry_surfaces.py tests/e2e/vision/test_reference_understanding_runtime_surface.py tests/e2e/integration/test_guided_gate_state_transport.py -q`

## Docs To Update

- `_docs/_MCP_SERVER/README.md` only if ownership wording or staged surface notes need maintenance updates
- `_docs/_VISION/README.md` if helper ownership notes currently point to the old monolith
- `_docs/_TASKS/README.md` only when the task status changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- `reference.py` no longer owns all planner/truth/silhouette/view/checkpoint
  helper logic directly
- the public staged MCP surface and response contracts remain stable
- provider registration and manifest-backed discovery for the reference family
  remain unchanged
- pure planner/truth helper logic has a clear home instead of remaining trapped
  in one adapter file by default
- targeted unit/integration/e2e lanes prove no staged-loop regression

## Status / Board Update

- keep promoted tracking on the parent `TASK-159`
- execute this subtask through the leaves below rather than as one monolithic
  refactor pass
- do not promote this slice independently unless it becomes the only remaining
  open branch in the family
