# TASK-135-03-02-01: Refinement Visibility Search And Planner Routing

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-135-03-02](./TASK-135-03-02_Bounded_Profile_Tools_And_Optional_Macro_Wave.md)
**Depends On:** [TASK-135-03-01](./TASK-135-03-01_Refinement_Stage_State_And_Visibility_Gate.md)
**Objective:** Wire the explicit `refine_low_poly_forms` step into existing visibility, discovery, and checkpoint planner routes using already-shipped mesh/modeling/macro tools only.
**Acceptance Criteria:** the refinement step exposes bounded profile-capable tools, search returns those same tools for low-poly body/ear/limb/snout/tail queries, planner route/handoff stays on `modeling_mesh` or `macro` for deterministic blockers, and broad sculpt remains hidden by default.

## Repository Touchpoints

| Path / Module | Owner Seam / Current Lines | Change Contract |
|---------------|----------------------------|-----------------|
| `server/adapters/mcp/transforms/visibility_policy.py` | `build_visibility_rules(...)` at `visibility_policy.py:591`; `visible_tools_for_gate_plan(...)` at `visibility_policy.py:702`; `GUIDED_TOOL_FAMILY_MAP` around `visibility_policy.py:167` | Map `refine_low_poly_forms` blockers to existing bounded mesh/modeling/macro tools without broad sculpt exposure; resolve any tool whose current guided family is not allowed before exposing it |
| `server/adapters/mcp/discovery/search_surface.py` | `BlenderDiscoverySearchTransform._search(...)` at `search_surface.py:210`; `_active_gate_recovery_tools(...)` at `search_surface.py:263`; `search_tools(...)` closure at `search_surface.py:308`; `build_search_transform(...)` at `search_surface.py:435` | Keep guided search constrained to currently visible/refinement-safe tools and active-gate recovery hints |
| `server/adapters/mcp/discovery/search_documents.py` | discovery entries for mesh/modeling/scene macro tools | Add low-poly profile, facet, ear, limb, snout, and tail search cues for shipped tools |
| `server/adapters/mcp/areas/reference_planner.py` | `select_refinement_route(...)` at `reference_planner.py:542`; `build_refinement_handoff(...)` at `reference_planner.py:672`; `LOW_POLY_HINTS` at `reference_planner.py:60` | Keep low-poly/faceted profile work on `modeling_mesh`; prefer `macro` only for assembly/truth blockers |
| `server/adapters/mcp/areas/reference.py` | checkpoint route/handoff projection around `reference.py:1490` | Surface route/handoff details on staged checkpoint and iterate responses |
| `server/adapters/mcp/router_helper.py` | guided execution-policy decision around `router_helper.py:757` | Ensure newly visible refinement mutators are mapped to allowed guided families before exposure |
| `server/router/infrastructure/tools_metadata/**` | mesh/modeling/scene metadata JSON | Add or update hints only for tools actually exposed by this leaf |
| `tests/unit/adapters/mcp/test_visibility_policy.py` | visibility fixtures | Assert active refinement blockers expose bounded tools and keep sculpt hidden |
| `tests/unit/adapters/mcp/test_search_surface.py` | discovery/search assertions | Assert low-poly profile queries return the same bounded tools as visibility allows |
| `tests/unit/adapters/mcp/test_reference_images.py` | route/handoff fixtures | Assert checkpoint planner route and feedback selected family align with active blockers |
| `tests/unit/adapters/mcp/test_context_bridge.py` | guided mutator enforcement | Assert exposed refinement mutators are accepted only in the mapped guided family |
| `tests/e2e/integration/test_guided_streamable_spatial_support.py` and `test_guided_surface_contract_parity.py` | transport proof | Assert stdio and Streamable expose the same refinement-safe tool set |

## Implementation Notes

- Do not introduce new public tools in this leaf.
- Treat `refine_low_poly_forms` as a visibility/search/planner state over the
  existing public surface.
- Keep `ReferencePlannerFamilyLiteral` values separate from
  `GuidedFlowFamilyLiteral`; planner route may say `modeling_mesh`, while
  guided visibility still uses existing guided families.
- `modeling_transform_object` currently maps to the `primary_masses` guided
  family. Do not expose it as a refinement tool unless this leaf either keeps
  `primary_masses` deliberately allowed while proving primitive-creation tools
  stay hidden/blocked, or changes the guided-family mapping/override with
  explicit context-bridge tests.
- If visibility cannot expose a needed existing tool without widening a family,
  record the exact family/tool mismatch before changing the vocabulary.

## Pseudocode

```python
if guided_flow_state.current_step != "refine_low_poly_forms":
    return build_visibility_rules_without_refinement_override()

route = select_refinement_route(checkpoint_result)
gate_tools = visible_tools_for_gate_plan(active_gate_plan)

if route.selected_family == "modeling_mesh":
    refinement_tools = {
        "mesh_select",
        "mesh_select_targeted",
        "mesh_extrude_region",
        "mesh_loop_cut",
        "mesh_bevel",
        "mesh_symmetrize",
        "mesh_transform_selected",
    }
    if guided_family_allows("modeling_transform_object"):
        refinement_tools.add("modeling_transform_object")
elif route.selected_family == "macro":
    refinement_tools = gate_tools | {"macro_adjust_segment_chain_arc"}
else:
    refinement_tools = gate_tools

visible_tools = refinement_tools & tools_allowed_by_guided_family_policy()
search_index = rank_only_visible_refinement_tools(visible_tools)
```

## Runtime / Security Contract Notes

- Visibility level: public guided visibility/search only; no new public MCP
  entrypoint.
- Read-only vs mutating behavior: visibility, search, route, and handoff are
  read-only/session-state outputs. The tools they expose remain the mutating
  owners and must keep their existing side-effect/stale-state contracts.
- Mode and selection impact: this leaf does not perform Blender mutations; it
  must not change mode or selection.
- Transport/session assumptions: stdio and Streamable HTTP must see equivalent
  visible tools and route/handoff payloads for the same session state.
- Parameter validation: metadata/search additions must reference existing tool
  ids and pass router metadata validation.
- Recovery: unresolved or stale gate evidence keeps the route on
  `inspect_only` or blocker-specific repair tools instead of exposing a broad
  profile window.

## Tests To Add/Update

| Test File | Cases / Assertions |
|-----------|--------------------|
| `tests/unit/adapters/mcp/test_visibility_policy.py` | `refine_low_poly_forms` exposes bounded mesh/modeling tools only after blockers permit refinement |
| `tests/unit/adapters/mcp/test_visibility_policy.py` | `modeling_transform_object` remains hidden unless its guided-family mapping or allowed-family policy is explicitly changed for refinement |
| `tests/unit/adapters/mcp/test_visibility_policy.py` | sculpt tools remain hidden unless the planner emits an explicit sculpt handoff from the existing `TASK-145` path |
| `tests/unit/adapters/mcp/test_search_surface.py` | "profile low-poly ear/limb/snout/tail" queries return bounded existing tools and do not return hidden broad tools |
| `tests/unit/adapters/mcp/test_reference_images.py` | low-poly/faceted checkpoint candidates keep `selected_family="modeling_mesh"` unless relation/macro blockers dominate |
| `tests/unit/adapters/mcp/test_context_bridge.py` | exposed mutators are accepted only through mapped guided families, and unmapped `primary_masses` mutators remain blocked during refinement |
| `tests/e2e/integration/test_guided_surface_contract_parity.py` | live stdio surface exposes the same refinement-safe tools as the contract tests expect |
| `tests/e2e/integration/test_guided_streamable_spatial_support.py` | Streamable HTTP guided surface returns the same visible refinement/search behavior |

## Docs To Update

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`
- `_docs/_CHANGELOG/README.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry if this leaf changes public guided
  visibility, search, or planner behavior.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_context_bridge.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py tests/e2e/integration/test_guided_streamable_spatial_support.py -q`
- `Outside sandbox before closeout: PYTHONPATH=. poetry run pytest ./tests/unit`

## Status / Board Update

- When this leaf ships, update its status plus the parent
  `TASK-135-03-02` execution structure and record whether `_docs/_TASKS/README.md`
  board wording changed.
