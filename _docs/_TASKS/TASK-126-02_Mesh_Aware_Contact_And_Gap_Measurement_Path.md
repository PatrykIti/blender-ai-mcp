# TASK-126-02: Mesh-Aware Contact and Gap Measurement Path

**Parent:** [TASK-126](./TASK-126_Mesh_Aware_Contact_Semantics_And_Visual_Fit_Reliability.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** `scene_measure_gap(...)`,
`scene_measure_overlap(...)`, and `scene_assert_contact(...)` now prefer a
mesh-surface contact/gap path for mesh-object pairs, while preserving bbox
fallback behavior for unsupported/non-mesh cases. This closes the core false
"touching/contact" failure mode for visibly gapped curved primitives.

## Objective

Add a more truthful contact/gap path for curved or rounded objects so the
truth layer can distinguish real surface fit from bounding-box coincidence.

## Business Problem

The current bbox-oriented contact model is too coarse for rounded primitives
and curved meshes.

That causes false positives such as:

- head/body reported as touching while the viewport still shows a gap
- eyes reported as surface-contacting while they visibly float
- tail/paws judged attached when only their bounding boxes meet

## Technical Direction

Implement one more truthful contact/gap path, likely mesh-aware or
surface-aware, and expose it in a way that can be consumed by:

- `scene_measure_*`
- `scene_assert_contact(...)`
- later macro/hybrid-loop consumers

The implementation should remain bounded and operationally safe.

## Repository Touchpoints

- `blender_addon/application/handlers/scene_handler.py`
- `server/application/tool_handlers/scene_handler.py`
- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/contracts/scene.py`
- `tests/unit/tools/scene/`
- `tests/e2e/tools/scene/`

## Acceptance Criteria

- the repo can distinguish bbox-touching from real surface/mesh fit for the
  targeted cases
- curved primitive pairs with visible gaps no longer pass as visually correct
  contact by default
- the new path is bounded, documented, and testable

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md` if hybrid consumers change

## Tests To Add/Update

- `tests/unit/tools/scene/`
- `tests/e2e/tools/scene/`

## Changelog Impact

- include in the parent task changelog entry when shipped
