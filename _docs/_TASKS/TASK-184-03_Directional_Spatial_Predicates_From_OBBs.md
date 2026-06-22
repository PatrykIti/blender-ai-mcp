# TASK-184-03: Directional Spatial Predicates From OBBs

**Parent:** [TASK-184](./TASK-184_Vision_3D_Understanding_Audit_Corrections.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Add deterministic, frame-tagged directional predicates to the spatial graph so LLMs can ask for structured left/right/front/behind-style facts without relying on object names or screenshots.

**Repository Touchpoints:** `server/application/services/spatial_graph.py`, `server/adapters/mcp/areas/scene_spatial_graph.py`, `server/adapters/mcp/areas/scene.py`, `server/adapters/mcp/contracts/scene.py`, `server/router/infrastructure/tools_metadata/scene/`, `tests/unit/tools/scene/test_spatial_graph_service.py`, `tests/unit/tools/scene/test_scene_contracts.py`, `_docs/_MCP_SERVER/README.md`, `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Implementation Notes

- Add a typed directional semantics contract rather than overloading
  `SceneRelationKindLiteral`.
- Wire the new semantics through `route_scene_relation_graph(...)` in
  `scene_spatial_graph.py`; `scene.py` is only the public facade wrapper for
  this route.
- At minimum support:
  - `direction_world`: deterministic axis relation in world space
  - optional `direction_camera`: view-relative relation when a reference camera
    is supplied
  - `reference_frame`, `reference_camera_name`, `axis`, `margin`, and
    `ambiguous` fields
- Use object bounding volumes/centers and explicit thresholds. Do not infer
  direction from names such as `LeftLeg`.
- Keep directional facts additive alongside existing contact/gap/alignment/
  attachment/support/symmetry facts.

## Runtime / Security Contract Notes

- unframed `left`, `right`, `front`, and `behind` labels are invalid in public
  contracts
- camera-relative direction must identify the camera/view frame used
- ambiguous or near-equal cases must be marked ambiguous rather than forced into
  a relation

## Tests To Add/Update

- spatial graph unit tests for world-frame left/right/front/behind and
  ambiguous thresholds
- contract round-trip tests for optional camera-frame directional semantics
- public docs tests if the tool inventory validates scene relation payloads

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_VISION/README.md`
- `TASK-143` or `TASK-181` historical follow-on note if needed

## Acceptance Criteria

- `scene_relation_graph(...)` can expose deterministic directional predicates
  with reference-frame metadata
- no existing relation graph consumer regresses when directional semantics are
  absent
- tests prove name hints alone cannot create directional truth

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_spatial_graph_service.py tests/unit/tools/scene/test_scene_contracts.py -q`
