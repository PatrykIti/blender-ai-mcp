# TASK-135-03-02: Bounded Profile Tools And Optional Macro Wave

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-135-03](./TASK-135-03_Low_Poly_Form_Refinement_Mesh_Window_And_Profile_Macros.md)
**Depends On:** [TASK-135-03-01](./TASK-135-03-01_Refinement_Stage_State_And_Visibility_Gate.md)
**Objective:** Make the refinement stage operational by exposing the right bounded mesh/modeling tools and only the smallest necessary macro additions for low-poly creature profiling.
**Repository Touchpoints:** `server/adapters/mcp/areas/mesh.py`, `server/adapters/mcp/areas/modeling.py`, `server/adapters/mcp/areas/scene.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/transforms/visibility_policy.py`, `server/adapters/mcp/router_helper.py`, `server/adapters/mcp/discovery/search_surface.py`, `server/router/infrastructure/tools_metadata/mesh/`, `server/router/infrastructure/tools_metadata/modeling/`, `server/router/infrastructure/tools_metadata/scene/`, `server/application/tool_handlers/macro_handler.py`, `server/domain/tools/macro.py`, `server/adapters/mcp/dispatcher.py`, `blender_addon/application/handlers/mesh.py`, `blender_addon/application/handlers/modeling.py`, `tests/unit/adapters/mcp/test_visibility_policy.py`, `tests/unit/adapters/mcp/test_search_surface.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/unit/adapters/mcp/test_guided_mode.py`, `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`, `tests/unit/adapters/mcp/test_public_surface_docs.py`, `tests/unit/tools/scene/test_macro_adjust_segment_chain_arc_mcp.py`, `tests/e2e/tools/macro/test_macro_adjust_segment_chain_arc.py`, `tests/e2e/vision/test_reference_stage_truth_handoff.py`
**Repository Touchpoints:** `server/adapters/mcp/areas/mesh.py`, `server/adapters/mcp/areas/modeling.py`, `server/adapters/mcp/areas/scene.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/transforms/visibility_policy.py`, `server/adapters/mcp/router_helper.py`, `server/adapters/mcp/discovery/search_surface.py`, `server/router/infrastructure/tools_metadata/mesh/`, `server/router/infrastructure/tools_metadata/modeling/`, `server/router/infrastructure/tools_metadata/scene/`, `server/application/tool_handlers/macro_handler.py`, `server/domain/tools/macro.py`, `server/adapters/mcp/dispatcher.py`, `blender_addon/application/handlers/mesh.py`, `blender_addon/application/handlers/modeling.py`, `tests/unit/adapters/mcp/test_visibility_policy.py`, `tests/unit/adapters/mcp/test_search_surface.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/unit/adapters/mcp/test_guided_mode.py`, `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`, `tests/unit/adapters/mcp/test_public_surface_docs.py`, `tests/unit/tools/macro/test_macro_adjust_segment_chain_arc.py`, `tests/unit/tools/scene/test_macro_adjust_segment_chain_arc_mcp.py`, `tests/e2e/tools/macro/test_macro_adjust_segment_chain_arc.py`, `tests/e2e/vision/test_reference_stage_truth_handoff.py`
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
- start by wiring the refinement window through the existing owner seams:
  - `visible_tools_for_gate_plan(...)` and `build_visibility_rules(...)` in
    `server/adapters/mcp/transforms/visibility_policy.py`
  - `build_search_transform(...)` in
    `server/adapters/mcp/discovery/search_surface.py`
  - `macro_adjust_segment_chain_arc(...)` on the current
    `server/adapters/mcp/areas/scene.py` macro surface
  - `_select_refinement_route(...)` coverage in
    `tests/unit/adapters/mcp/test_reference_images.py`, especially the current
    low-poly creature branch that prefers `modeling_mesh`
- treat candidate names such as `macro_refine_creature_part_profile`,
  `macro_point_creature_ears`, `macro_flatten_limb_contact_patch`, and
  `macro_add_creature_eye_pair` as optional follow-ons, not assumed shipped
  tools
- add a new macro only when:
  - the bounded mesh/modeling window cannot express the move safely enough
  - the move recurs across multiple creature profile repairs
  - the macro can stay deterministic and role-aware
- treat one concrete escalation trigger as mandatory before adding a macro: the
  repair still requires repeated free-form multi-step selection/setup or unsafe
  mesh-mode choreography after `mesh_select` / `mesh_select_targeted(...)` plus
  one bounded modeling/mesh mutation, and the same failure recurs across more
  than one creature part class
- if escalation happens, keep the macro on the current public scene-macro
  surface and update `server/domain/tools/macro.py`,
  `server/application/tool_handlers/macro_handler.py`,
  `server/adapters/mcp/areas/scene.py`, `server/adapters/mcp/dispatcher.py`,
  `server/adapters/mcp/transforms/visibility_policy.py`, and guided execution
  enforcement in `server/adapters/mcp/router_helper.py`, plus router metadata,
  docs, and tests in the same slice. Only touch addon or DI layers if the
  macro cannot be composed from the current modeling/scene RPC path
- keep discoverability aligned across metadata, `search_surface`, and guided
  visibility; do not rely on docs-only naming

## Runtime / Security Contract Notes

- Visibility level: keep the refinement tool window on the existing guided
  visibility/search surfaces. Do not expose broad sculpt here, and do not add a
  second discovery path for profile work.
- Read-only vs mutating behavior: visibility/search hints and
  `refinement_route` outputs are server/session-state only. Mesh/modeling/macro
  operations remain the mutating Blender paths and must mark affected
  shape-profile evidence stale after execution.
- Mode and selection impact: profile work may enter edit mode, but the first
  slice must keep selection setup bounded and restore the caller's expected mode
  or selection through the current guided runtime helpers before returning.
- Session and auth assumptions: refinement-tool exposure stays scoped to the
  active stdio or Streamable HTTP session, with local Blender RPC as the only
  trusted mutating backend.
- Parameter validation and compatibility: visible tool ids, search metadata, and
  any new macro arguments use strict typed contracts with reject-unknown
  behavior. Compatibility shims stay explicit in the owning contract layer.
- Side effects, recovery, and logging: no free-form “profile anything” macro may
  bypass current family or role gating. When a concrete repair still needs broad
  free-form edits, keep the task blocked or escalate through explicit follow-on
  scope instead of silently widening the tool surface. Keep provider keys or
  local paths out of logs.
- Resource and timeout limits: keep one refinement slice bounded to local
  profile operations on the active target scope; no macro may fan out across an
  unbounded object set or run repeated mesh/setup loops after one checkpoint
  decision.

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/tools/macro/test_macro_adjust_segment_chain_arc.py`
- `tests/unit/tools/scene/test_macro_adjust_segment_chain_arc_mcp.py`
- `tests/e2e/tools/macro/test_macro_adjust_segment_chain_arc.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- targeted `tests/unit/tools/mesh/` or `tests/unit/tools/modeling/` lanes when
  a concrete bounded profile operation changes

## Docs To Update

- `README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_CHANGELOG/README.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when the first new refinement macro or
  bounded profile-tool exposure ships.

## Validation Commands

- `git diff --check`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_guided_surface_benchmarks.py tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/tools/macro/test_macro_adjust_segment_chain_arc.py tests/unit/tools/scene/test_macro_adjust_segment_chain_arc_mcp.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/tools/macro/test_macro_adjust_segment_chain_arc.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_stage_truth_handoff.py -q`
- `Outside sandbox before closeout: PYTHONPATH=. poetry run pytest ./tests/unit`
- `Outside sandbox for Blender-backed runtime proof: poetry run python scripts/run_e2e_tests.py`

## Status / Board Update

- When this leaf ships, update its task status plus the parent `TASK-135-03`
  execution structure and note whether public guided-surface wording changed in
  `_docs/_TASKS/README.md` or the parent task files.
- Record whether the `pre-commit` lane, owner-lane pytest commands, full unit
  pass, and full Blender E2E pass ran or were intentionally skipped.
- If the bounded-tool slice still leaves a promoted macro or extra runtime lane
  open, track that as a separate follow-on leaf rather than leaving the current
  status partially implied.
