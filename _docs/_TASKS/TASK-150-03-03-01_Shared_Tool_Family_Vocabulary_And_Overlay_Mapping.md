# TASK-150-03-03-01: Shared Tool Family Vocabulary And Overlay Mapping

**Parent:** [TASK-150-03-03](./TASK-150-03-03_Generic_Families_Part_Roles_And_Execution_Enforcement.md)
**Status:** 🚧 In Progress
**Priority:** 🔴 High

## Objective

Define one shared family vocabulary for post-bootstrap guided build work so
the server can talk about `primary_masses`, `secondary_parts`,
`attachment_alignment`, `checkpoint_iterate`, `inspect_validate`, and
`finish` without creating domain-specific tool families from scratch.

## Repository Touchpoints

- `server/adapters/mcp/contracts/guided_flow.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/router_helper.py`

## Acceptance Criteria

- one stable family vocabulary exists for guided execution policy
- overlays map existing tools/macros onto those families
- `generic`, `creature`, and `building` can differ in family ordering and
  allowed roles without forking the family vocabulary itself

## Detailed Implementation Notes

- keep the family set intentionally small and generic
- avoid names like `creature_ears` or `building_window_cutouts` at the family
  layer; those belong in role/group metadata, not the shared family system
- current likely family set:
  - `spatial_context`
  - `reference_context`
  - `primary_masses`
  - `secondary_parts`
  - `attachment_alignment`
  - `checkpoint_iterate`
  - `inspect_validate`
  - `finish`
  - `utility`
- this leaf should define:
  - family identifiers
  - tool-to-family mapping
  - per-overlay family order / allowed family windows

## Current Code Anchors

- `server/adapters/mcp/contracts/guided_flow.py`
  - lines 12-23: current domain/step/status literals
  - lines 36-48: current public `GuidedFlowStateContract`
- `server/adapters/mcp/session_capabilities.py`
  - lines 196-210: current domain-profile selection
  - lines 252-314: current guided-flow initialization
- `server/adapters/mcp/transforms/visibility_policy.py`
  - lines 452-499: current guided visibility construction

## Pseudocode Sketch

```python
GuidedFlowFamilyLiteral = Literal[
    "spatial_context",
    "reference_context",
    "primary_masses",
    "secondary_parts",
    "attachment_alignment",
    "checkpoint_iterate",
    "inspect_validate",
    "finish",
    "utility",
]

TOOL_FAMILY_MAP = {
    "scene_scope_graph": "spatial_context",
    "scene_relation_graph": "spatial_context",
    "scene_view_diagnostics": "spatial_context",
    "reference_images": "reference_context",
    "modeling_create_primitive": "primary_masses",
    "modeling_transform_object": "primary_masses",
    "macro_align_part_with_contact": "attachment_alignment",
    "reference_iterate_stage_checkpoint": "checkpoint_iterate",
    "macro_finish_form": "finish",
}

OVERLAY_FAMILY_ORDER = {
    "creature": (
        "spatial_context",
        "reference_context",
        "primary_masses",
        "secondary_parts",
        "attachment_alignment",
        "checkpoint_iterate",
        "inspect_validate",
        "finish",
    ),
}
```

## Planned Unit Test Scenarios

- contract accepts only the intended family literals
- `creature` overlay maps `modeling_create_primitive` and
  `modeling_transform_object` into `primary_masses`
- `building` overlay maps finish-family tools later than
  `create_primary_masses`
- visibility policy can expose `allowed_families` in step-aware summaries

## Planned E2E / Transport Scenarios

- stdio guided creature session keeps `scene_*` spatial tools visible during
  `establish_spatial_context` while `finish` tools stay unavailable
- after family unlock, transport-backed status payloads show the expected
  family order for the active overlay

## Execution Structure

| Order | Micro-Leaf | Purpose |
|------|------------|---------|
| 1 | [TASK-150-03-03-01-01](./TASK-150-03-03-01-01_Guided_Family_Literals_And_Flow_Contract_Extension.md) | Extend the shared guided-flow contract with a stable family vocabulary |
| 2 | [TASK-150-03-03-01-02](./TASK-150-03-03-01-02_Tool_To_Family_Mapping_And_Overlay_Family_Order.md) | Map existing tools/macros onto families and encode per-overlay family order |

## Docs To Update

- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`

## Changelog Impact

- include in the parent TASK-150 execution-enforcement changelog entry
