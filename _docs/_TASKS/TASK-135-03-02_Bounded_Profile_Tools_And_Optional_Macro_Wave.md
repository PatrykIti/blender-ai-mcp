# TASK-135-03-02: Bounded Profile Tools And Optional Macro Wave

**Status:** ✅ Done
**Priority:** 🔴 High
**Parent:** [TASK-135-03](./TASK-135-03_Low_Poly_Form_Refinement_Mesh_Window_And_Profile_Macros.md)
**Depends On:** [TASK-135-03-01](./TASK-135-03-01_Refinement_Stage_State_And_Visibility_Gate.md)
**Objective:** Decompose the bounded profile-tool wave into focused leaves so the refinement stage becomes operational without bundling visibility, search, planner routing, geometry proof, and optional macro promotion into one oversized implementation pass.
**Acceptance Criteria:** the child leaves separately cover refinement visibility/search/planner routing, proof that existing mesh/modeling/macro tools can profile common creature parts, and optional macro promotion only after proof shows a repeated unsafe choreography gap.

## Repository Touchpoints

| Path / Module | Owner Seam / Current Lines | Change Contract |
|---------------|----------------------------|-----------------|
| `server/adapters/mcp/transforms/visibility_policy.py` | `build_visibility_rules(...)` at `visibility_policy.py:591`; `visible_tools_for_gate_plan(...)` at `visibility_policy.py:702` | Child `03-02-01` owns refinement blocker visibility with existing tools only |
| `server/adapters/mcp/discovery/search_surface.py` and `search_documents.py` | `build_search_transform(...)` at `search_surface.py:435`; discovery entries | Child `03-02-01` owns low-poly profile search results |
| `server/adapters/mcp/areas/reference_planner.py` | `select_refinement_route(...)` at `reference_planner.py:542`; `build_refinement_handoff(...)` at `reference_planner.py:672` | Child `03-02-01` owns `modeling_mesh` / `macro` / `inspect_only` route alignment |
| `server/adapters/mcp/areas/mesh.py` and `modeling.py` | bounded mesh/modeling wrappers | Child `03-02-02` owns proof that existing tools can profile body, ears, limbs, snout, and tail candidates |
| `server/adapters/mcp/areas/scene.py` | `macro_adjust_segment_chain_arc(...)` at `scene.py:881`; attach/align macros | Child `03-02-02` owns reuse proof; child `03-02-03` touches only if a new macro is promoted |
| `server/adapters/mcp/router_helper.py` | guided execution-policy decision around `router_helper.py:757` | Child `03-02-01` / `03-02-03` owns mutator family mapping when visible tools change |
| `server/router/infrastructure/tools_metadata/**` | mesh/modeling/scene metadata JSON | Child leaves update metadata only for shipped visible tools or promoted macros |
| `server/domain/tools/macro.py`, `server/application/tool_handlers/macro_handler.py`, `server/adapters/mcp/dispatcher.py` | macro interface/handler/dispatcher seams | Child `03-02-03` owns optional profile macro promotion only |
| `blender_addon/application/handlers/mesh.py` and `modeling.py` | addon-side handlers | Child `03-02-02` or `03-02-03` touches only when new Blender behavior is required |
| Test lanes | visibility/search/planner tests, mesh/modeling/macro unit tests, Streamable/stdio E2E, Blender-backed geometry tests | Each child leaf owns exact cases below and in its own file |

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-135-03-02-01](./TASK-135-03-02-01_Refinement_Visibility_Search_And_Planner_Routing.md) | ✅ Closed: refinement visibility/search/planner routing now stays on the bounded existing-tool surface |
| 2 | [TASK-135-03-02-02](./TASK-135-03-02-02_Existing_Profile_Tool_Proof_And_Geometry_Cases.md) | ✅ Closed: Blender-backed proof covers body, ear, snout, limb, and tail profile cases without a new macro |
| 3 | [TASK-135-03-02-03](./TASK-135-03-02-03_Optional_Profile_Macro_Promotion.md) | ⏭️ Superseded: no repeated unsafe choreography remained after the existing-tool proof wave |

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

## Pseudocode

```python
if current_step != "refine_low_poly_forms":
    return current_visibility_and_search_surface()

route = select_refinement_route(checkpoint_result)
if route.blockers:
    expose_tools = visible_tools_for_gate_plan(active_gate_plan)
else:
    expose_tools = bounded_profile_tools_for(route.selected_family)

search_documents = rank_profile_tools(
    query_terms=["low-poly", "profile", "ear", "limb", "snout", "tail"],
    allowed_tools=expose_tools,
)

if existing_tools_can_complete_profile_cases:
    close_without_new_macro()
else:
    open TASK-135-03-02-03 with the repeated choreography gap as evidence
```

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

| Child Leaf | Required Cases |
|------------|----------------|
| `TASK-135-03-02-01` | visibility/search/planner unit tests for refinement blockers, low-poly profile queries, sculpt-hidden default, context-bridge mutator enforcement, and stdio/Streamable visible-tool parity |
| `TASK-135-03-02-02` | unit and Blender E2E proof for selected existing mesh/modeling/macro operations on representative body, ear, limb, snout, and tail profile cases |
| `TASK-135-03-02-03` | macro interface, MCP wrapper, dispatcher, metadata, addon/handler, unit, Streamable, and Blender E2E tests only when a new macro is promoted |

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_PROMPTS/MANUAL_TOOLS_NO_ROUTER.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_VISION/README.md`
- relevant `_docs/_VISION/*` creature and refinement docs enforced by
  `test_public_surface_docs.py` when public guided-surface wording changes
- `_docs/_CHANGELOG/README.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when the first new refinement macro or
  bounded profile-tool exposure ships.

## Validation Commands

- `git diff --check`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_guided_surface_benchmarks.py tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/tools/macro/test_macro_adjust_segment_chain_arc.py tests/unit/tools/scene/test_macro_adjust_segment_chain_arc_mcp.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/tools/macro/test_macro_adjust_segment_chain_arc.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_streamable_spatial_support.py tests/e2e/vision/test_reference_stage_truth_handoff.py -q`
- `Outside sandbox before closeout: PYTHONPATH=. poetry run pytest ./tests/unit`
- `Outside sandbox for Blender-backed runtime proof: poetry run python scripts/run_e2e_tests.py`

## Status / Board Update

- `TASK-135-03-02` is closed after both direct implementation leaves shipped
  and the optional macro leaf was superseded.
- No `_docs/_TASKS/README.md` board wording change was required for this nested
  subtask because only the board-level umbrella row tracks `TASK-135`.

## Completion Summary

- 2026-05-11: The refinement step now discovers bounded mesh/profile tools for
  low-poly creature body, ear, limb, snout, and tail work without widening the
  public surface.
- Blender-backed proof confirms that the shipped mesh and macro tools are
  enough for the first representative creature profile cases.
- The profile-tool wave closed without a new public macro; the existing bounded
  surface remained sufficient.
