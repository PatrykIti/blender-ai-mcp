# TASK-135-03-01: Refinement Stage State And Visibility Gate

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-135-03](./TASK-135-03_Low_Poly_Form_Refinement_Mesh_Window_And_Profile_Macros.md)
**Objective:** Add one explicit low-poly refinement stage to the current creature guided flow so the runtime can open a bounded mesh/modeling window only after required roles and seams are stable enough.
**Repository Touchpoints:** `server/adapters/mcp/session_capabilities.py`, `server/adapters/mcp/contracts/guided_flow.py`, `server/adapters/mcp/session_capabilities_registry.py`, `server/adapters/mcp/session_capabilities_state.py`, `server/adapters/mcp/session_capabilities_flow.py`, `server/adapters/mcp/session_capabilities_runtime_glue.py`, `server/adapters/mcp/transforms/visibility_policy.py`, `server/adapters/mcp/contracts/quality_gates.py`, `server/adapters/mcp/areas/reference.py`, `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`, `tests/unit/adapters/mcp/test_visibility_policy.py`, `tests/unit/adapters/mcp/test_router_elicitation.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_guided_mode.py`, `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`, `tests/unit/adapters/mcp/test_public_surface_docs.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/vision/test_reference_stage_truth_handoff.py`
**Acceptance Criteria:** the creature domain can advance into one explicit refinement step after prerequisite masses and seams are stable; the refinement step keeps `guided_flow_state.allowed_families` on the existing guided-family vocabulary while checkpoint-local planner outputs may still recommend `modeling_mesh` or `macro`; stage/gate state survives session persistence and transport.

## Implementation Notes

- keep `server/adapters/mcp/session_capabilities.py` as the stable facade, but
  implement the real state/policy changes in the split session-capability
  modules
- add one explicit creature refinement step such as `refine_low_poly_forms`
  rather than overloading `place_secondary_parts` or `finish_or_stop`
- update `GuidedFlowStepLiteral` / `GuidedFlowFamilyLiteral` in
  `server/adapters/mcp/contracts/guided_flow.py` together with the real step
  advancement paths in
  `server/adapters/mcp/session_capabilities_registry.py`, especially
  `_maybe_advance_guided_flow_from_part_registry_dict(...)` and the
  checkpoint-outcome transitions that currently move creature work from
  `place_secondary_parts` toward `checkpoint_iterate`
- gate entry on normalized `TASK-157` status, for example:
  - required primary and secondary roles registered
  - required creature seams no longer blocking
  - the session is not currently stale on spatial/gate refresh
- project the new step through current `guided_flow_state`,
  `active_gate_plan`, and visibility/search shaping; do not invent a parallel
  creature-only state envelope
- keep the vocabulary split explicit:
  - `guided_flow_state.allowed_families` continues to use
    `GuidedFlowFamilyLiteral`
  - `refinement_route.selected_family` and
    `reference_strategy_state.primary_family` keep the planner-facing
    `ReferencePlannerFamilyLiteral`; `reference_understanding_summary`
    separately keeps its own `construction_strategy.primary_family`
- keep sculpt hidden on this step unless a later `TASK-145` handoff explicitly
  recommends bounded local sculpt

## Pseudocode

```python
if domain_profile == "creature" and current_step == "place_secondary_parts":
    if required_roles_ready and required_creature_seams_stable:
        advance_to("refine_low_poly_forms")

if current_step == "refine_low_poly_forms":
    guided_allowed_families = [
        "secondary_parts",
        "attachment_alignment",
        "reference_context",
    ]
    planner_selected_family = "modeling_mesh"
    planner_blocked_families = ["sculpt_region"]
```

## Runtime / Security Contract Notes

- Visibility level: reuse the shipped public `guided_flow_state` and
  `active_gate_plan` contracts and the current guided visibility surfaces; do
  not expose a new public MCP tool just to enter or inspect the refinement
  stage.
- Read-only vs mutating behavior: entering or reporting the refinement stage is
  server/session-state only. Existing modeling, mesh, scene, and macro tools
  remain the only mutating Blender paths and must mark refinement evidence
  stale when they change scene state.
- Mode and selection impact: stage entry or visibility changes must not disturb
  the current active object, mode, or selection. Mutating tools opened by this
  stage must restore the expected state through the existing guided runtime
  helpers.
- Session and auth assumptions: refinement-step state stays scoped to the
  active stdio or Streamable HTTP session, with local Blender RPC as the only
  trusted mutating backend.
- Parameter validation and compatibility: step names, family literals, and gate
  prerequisites use strict typed contracts with reject-unknown behavior.
  Compatibility shims stay explicit in the owning contract layer.
- Side effects, recovery, and logging: keep verifier authority on the existing
  `TASK-157` gate path. Stage entry is a policy decision over normalized gate
  status, not perception confidence. If prerequisites are stale or unresolved,
  keep the flow blocked or in `inspect_validate` instead of silently advancing,
  and keep provider keys or local paths out of logs.
- Resource and timeout limits: keep the refinement-step transition bounded to
  the currently active creature scope and one staged checkpoint cadence; do not
  add background refresh loops or repeated gate recomputation beyond the
  existing guided refresh boundaries.

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`

## Docs To Update

- `README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_CHANGELOG/README.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when the explicit refinement step ships.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_router_elicitation.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_guided_surface_benchmarks.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_stage_truth_handoff.py -q`
- `Outside sandbox before closeout: PYTHONPATH=. poetry run pytest ./tests/unit`
- `Outside sandbox for Blender-backed runtime proof: poetry run python scripts/run_e2e_tests.py`
