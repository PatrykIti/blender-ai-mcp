# TASK-128-01-03: Creature-Aware Guided Handoff and Tool Recipes

**Parent:** [TASK-128-01](./TASK-128-01_Guided_Creature_Prompting_Handoff_And_Discovery_Hints.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Define an explicit creature-oriented `guided_manual_build` handoff so
`llm-guided` stops relying on a broad macro-first surface for low-poly and
early organic creature blockout.

## Technical Direction

Planned recipe sets:

- `low_poly_creature_blockout`
  - `collection_manage`
  - `modeling_create_primitive`
  - `modeling_transform_object`
  - `scene_set_active_object`
  - `scene_set_mode`
  - `mesh_select`
  - `mesh_select_targeted`
  - `mesh_extrude_region`
  - `mesh_loop_cut`
  - `mesh_bevel`
  - `mesh_symmetrize`
  - `mesh_merge_by_distance`
  - `mesh_dissolve`
  - `macro_adjust_relative_proportion`
  - `macro_adjust_segment_chain_arc`
  - `macro_align_part_with_contact`
  - `macro_cleanup_part_intersections`
  - `reference_iterate_stage_checkpoint`
  - `scene_measure_dimensions`
  - `scene_assert_proportion`
  - `scene_get_viewport`
  - `inspect_scene`
- `mid_poly_organic_refine`
  - all of the above where relevant
  - `mesh_subdivide`
  - `mesh_edge_slide`
  - `mesh_vert_slide`
  - `mesh_tris_to_quads`
  - `macro_finish_form`

The slice should keep sculpt as a later bounded handoff, not as the default
creature starting surface.

## Repository Touchpoints

- `server/adapters/mcp/transforms/visibility_policy.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/router/application/test_router_contracts.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_session_phase.py`
- `tests/e2e/router/test_guided_manual_handoff.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Acceptance Criteria

- `guided_manual_build` handoff can expose a bounded creature-oriented tool set
- low-poly creature work favors modeling/mesh tools before sculpt exposure
- docs explain the intended creature recipe sets and why they are bounded

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/router/application/test_router_contracts.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_session_phase.py`
- `tests/e2e/router/test_guided_manual_handoff.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-128-01-03-01](./TASK-128-01-03-01_Low_Poly_Creature_Blockout_Recipe.md) | Define the low-poly creature starter recipe for bounded guided build handoff |
| 2 | [TASK-128-01-03-02](./TASK-128-01-03-02_Mid_Poly_Organic_Refine_Recipe_And_Sculpt_Boundary.md) | Define the mid-poly follow-on recipe and keep sculpt as a later bounded handoff |
| 3 | [TASK-128-01-03-03](./TASK-128-01-03-03_Guided_Handoff_Payload_Visibility_And_Regression.md) | Convert the recipes into explicit payload/visibility behavior and regressions |
