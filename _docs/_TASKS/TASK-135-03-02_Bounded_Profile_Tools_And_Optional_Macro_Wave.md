# TASK-135-03-02: Bounded Profile Tools And Optional Macro Wave

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-135-03](./TASK-135-03_Low_Poly_Form_Refinement_Mesh_Window_And_Profile_Macros.md)
**Depends On:** [TASK-135-03-01](./TASK-135-03-01_Refinement_Stage_State_And_Visibility_Gate.md)
**Objective:** Make the refinement stage operational by exposing the right bounded mesh/modeling tools and only the smallest necessary macro additions for low-poly creature profiling.
**Repository Touchpoints:** `server/adapters/mcp/areas/mesh.py`, `server/adapters/mcp/areas/modeling.py`, `server/adapters/mcp/areas/scene.py`, `server/adapters/mcp/transforms/visibility_policy.py`, `server/adapters/mcp/discovery/search_surface.py`, `server/router/infrastructure/tools_metadata/mesh/`, `server/router/infrastructure/tools_metadata/modeling/`, `server/router/infrastructure/tools_metadata/scene/`, `server/application/tool_handlers/macro_handler.py`, `blender_addon/application/handlers/mesh.py`, `blender_addon/application/handlers/modeling.py`, `tests/unit/adapters/mcp/test_search_surface.py`, `tests/unit/tools/scene/test_macro_adjust_segment_chain_arc_mcp.py`, `tests/e2e/tools/macro/test_macro_adjust_segment_chain_arc.py`
**Acceptance Criteria:** the refinement step exposes a bounded profile-tool window; existing mesh/modeling tools cover the first slice unless one concrete missing profile operation forces a new macro; any new macro has matching MCP, handler, and Blender-backed tests.

## Implementation Notes

- start from existing tools:
  - `mesh_select`
  - `mesh_select_targeted`
  - `mesh_extrude_region`
  - `mesh_loop_cut`
  - `mesh_bevel`
  - `mesh_symmetrize`
  - bounded modeling transforms
  - `macro_adjust_segment_chain_arc(...)` for ordered appendage arcs
- treat candidate names such as `macro_refine_creature_part_profile`,
  `macro_point_creature_ears`, `macro_flatten_limb_contact_patch`, and
  `macro_add_creature_eye_pair` as optional follow-ons, not assumed shipped
  tools
- add a new macro only when:
  - the bounded mesh/modeling window cannot express the move safely enough
  - the move recurs across multiple creature profile repairs
  - the macro can stay deterministic and role-aware
- keep discoverability aligned across metadata, `search_surface`, and guided
  visibility; do not rely on docs-only naming

## Runtime / Security Contract Notes

- no broad sculpt exposure on the refinement step
- no free-form “profile anything” macro that bypasses current family and role
  gating
- any new macro must follow the normal MCP/app/domain/addon/test/documentation
  change playbook from `AGENTS.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/tools/scene/test_macro_adjust_segment_chain_arc_mcp.py`
- `tests/e2e/tools/macro/test_macro_adjust_segment_chain_arc.py`
- targeted `tests/unit/tools/mesh/` or `tests/unit/tools/modeling/` lanes when
  a concrete bounded profile operation changes

## Docs To Update

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when the first new refinement macro or
  bounded profile-tool exposure ships.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_search_surface.py tests/unit/tools/scene/test_macro_adjust_segment_chain_arc_mcp.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/tools/macro/test_macro_adjust_segment_chain_arc.py -q`
