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
- `server/adapters/mcp/vision/`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `tests/e2e/vision/test_goal_derived_gate_support_symmetry_surfaces.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`

## Implementation Notes

- Keep `reference.py` as the public MCP facade and staged response assembler.
- Move private helper clusters by concern, not one function at a time.
- If a helper does not need `Context`, MCP contracts, or adapter-only imports,
  evaluate promoting it into `server/application/services/`.
- Keep compare / iterate response assembly in one visible place so future
  implementers can still trace the response contract end to end.
- Do not widen staged payloads during the extraction. This task is about module
  boundaries, not feature growth.
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
- Do not leak provider keys, local paths, or oversized debug payloads while
  moving helpers.
- Preserve current budget-control behavior and trim semantics.

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `tests/e2e/vision/test_goal_derived_gate_support_symmetry_surfaces.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_stage_truth_handoff.py tests/e2e/vision/test_goal_derived_gate_support_symmetry_surfaces.py tests/e2e/integration/test_guided_gate_state_transport.py -q`

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
- pure planner/truth helper logic has a clear home instead of remaining trapped
  in one adapter file by default
- targeted unit/integration/e2e lanes prove no staged-loop regression

## Status / Board Update

- keep promoted tracking on the parent `TASK-159`
- do not promote this slice independently unless it becomes the only remaining
  open branch in the family
