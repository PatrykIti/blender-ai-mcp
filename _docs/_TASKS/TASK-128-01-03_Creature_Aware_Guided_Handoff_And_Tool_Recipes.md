# TASK-128-01-03: Creature-Aware Guided Handoff and Tool Recipes

**Parent:** [TASK-128-01](./TASK-128-01_Guided_Creature_Prompting_Handoff_And_Discovery_Hints.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Define an explicit creature-oriented `guided_manual_build` handoff so
`llm-guided` stops relying on a broad macro-first surface for low-poly and
early organic creature blockout.

## Current Runtime Baseline

The repo already emits typed `guided_manual_build` handoffs and preserves them
in session diagnostics. The remaining problem is that the current payload and
build-phase surface are still too broad for creature blockout.

## Current Drift To Resolve

Current audited drift is:

- `guided_handoff.direct_tools` still centers a generic macro-heavy set
- `BUILD` phase visibility expands into a large generic surface
- the task wording currently blurs two different concerns:
  - generic `BUILD` phase posture for non-creature sessions
  - creature-specific narrowing after a `guided_manual_build` handoff
- current regression tests mostly protect that broad baseline instead of a
  creature-oriented recipe

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

Technical clarification for implementation:

- do **not** redefine every `BUILD` session as a creature session
- instead, define one explicit creature-oriented `guided_manual_build`
  handoff/recipe path that becomes visible only when the active guided session
  is actually a creature blockout case
- the enforceable runtime seam should be:
  `router_set_goal(...)` result -> `guided_handoff` payload ->
  session state persistence -> session-applied visibility/search behavior
- regression scope should distinguish:
  - generic `BUILD` phase baseline
  - creature-handoff shaped baseline
- the task is complete only when that seam is explicit in both runtime touch
  points and regression coverage; docs-only recipe wording does not count

## Repository Touchpoints

- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/contracts/router.py`
- `server/adapters/mcp/guided_mode.py`
- `server/adapters/mcp/session_capabilities.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/router/application/test_router_contracts.py`
- `tests/unit/router/application/test_router_handler_parameters.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_session_phase.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/router/test_guided_manual_handoff.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Acceptance Criteria

- `guided_manual_build` handoff can expose a bounded creature-oriented tool set
- the first low-poly creature handoff is modeling/mesh-first and explicitly
  includes the expected blockout path (`modeling_create_primitive`,
  `modeling_transform_object`, `mesh_select`, `mesh_extrude_region`,
  `mesh_loop_cut`, and adjacent blockout tools) before finishing/sculpt tools
- low-poly creature work favors modeling/mesh tools before sculpt exposure
- session-applied visibility/search on that creature handoff is bounded to the
  shaped recipe instead of falling back to the broad generic `BUILD` surface
- docs explain the intended creature recipe sets, why they are bounded, and how
  that bounded handoff is surfaced on `llm-guided`
- regression coverage verifies the creature-oriented payload and does not treat
  the current broad generic build surface as the desired end state

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/router/application/test_router_contracts.py`
- `tests/unit/router/application/test_router_handler_parameters.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_session_phase.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/router/test_guided_manual_handoff.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-128-01-03-01](./TASK-128-01-03-01_Low_Poly_Creature_Blockout_Recipe.md) | Define the low-poly creature starter recipe for bounded guided build handoff |
| 2 | [TASK-128-01-03-02](./TASK-128-01-03-02_Mid_Poly_Organic_Refine_Recipe_And_Sculpt_Boundary.md) | Define the mid-poly follow-on recipe and keep sculpt as a later bounded handoff |
| 3 | [TASK-128-01-03-03](./TASK-128-01-03-03_Guided_Handoff_Payload_Visibility_And_Regression.md) | Convert the recipes into explicit payload/visibility behavior and regressions |
