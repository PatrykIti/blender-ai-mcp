# TASK-135-03-01: Refinement Stage State And Visibility Gate

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-135-03](./TASK-135-03_Low_Poly_Form_Refinement_Mesh_Window_And_Profile_Macros.md)
**Objective:** Add one explicit low-poly refinement stage to the current creature guided flow so the runtime can open a bounded mesh/modeling window only after required roles and seams are stable enough.
**Acceptance Criteria:** the creature domain can advance into one explicit refinement step after prerequisite masses and seams are stable; the refinement step keeps `guided_flow_state.allowed_families` on the existing guided-family vocabulary while checkpoint-local planner outputs may still recommend `modeling_mesh` or `macro`; stage/gate state survives session persistence and transport.

## Repository Touchpoints

| Path / Module | Owner Seam / Current Lines | Change Contract |
|---------------|----------------------------|-----------------|
| `server/adapters/mcp/contracts/guided_flow.py` | `GuidedFlowStepLiteral` at `guided_flow.py:24`; `GuidedFlowStateContract.current_step` at `guided_flow.py:63` | Add `refine_low_poly_forms`; reject unknown step names through the existing contract |
| `server/adapters/mcp/session_capabilities_flow.py` | `_build_allowed_families(...)` at `session_capabilities_flow.py:480`; `_flow_state_for_current_step(...)` at `session_capabilities_flow.py:634`; `_default_next_actions_for_step(...)` at `session_capabilities_flow.py:606` | Define allowed families, next actions, role summary, and step status for the new step |
| `server/adapters/mcp/session_capabilities_registry.py` | `_maybe_advance_guided_flow_from_part_registry_dict(...)` at `session_capabilities_registry.py:60`; current signature receives `flow_state` and `part_registry` only | Advance from `place_secondary_parts` to `refine_low_poly_forms` only after required roles are complete and required gate blockers are clear; either extend the call site to pass a normalized gate-blocker summary from session state or keep the gate check in a caller that already owns `active_gate_plan` |
| `server/adapters/mcp/session_capabilities_state.py` | `SessionCapabilityState` guided-flow serialization | Round-trip the new step, completed steps, gate plan, and stale markers |
| `server/adapters/mcp/session_capabilities_runtime_glue.py` | gate refresh / stale marking helpers | Ensure scene mutations make refinement evidence stale and do not preserve old pass states |
| `server/adapters/mcp/transforms/visibility_policy.py` | `build_visibility_rules(...)` at `visibility_policy.py:591`; `visible_tools_for_gate_plan(...)` at `visibility_policy.py:702` | Keep visibility bounded to refinement-safe families and gate-visible tools |
| `server/adapters/mcp/contracts/quality_gates.py` | `refinement_stage` vocabulary and default tools around `quality_gates.py:15` and `quality_gates.py:170` | Keep refinement as a generic gate type, not a creature-only status field |
| `server/adapters/mcp/areas/reference.py` | checkpoint route projection around `reference.py:1490` | Project the new step through staged checkpoint/iterate payloads without a parallel envelope |
| `tests/unit/adapters/mcp/test_guided_flow_state_contract.py` | guided state contract fixtures | Add round-trip, advancement, and stale-blocking cases |
| `tests/unit/adapters/mcp/test_visibility_policy.py` and `test_guided_mode.py` | guided visibility assertions | Assert mesh/modeling families are visible only for the refinement step and not while seam blockers remain |
| `tests/unit/adapters/mcp/test_reference_images.py` | checkpoint fixtures | Assert checkpoint/iterate outputs expose the refinement blocker/step consistently |
| `tests/e2e/integration/test_guided_gate_state_transport.py` and `tests/e2e/vision/test_reference_stage_truth_handoff.py` | transport/runtime proof | Prove stdio/Streamable payloads and staged truth handoff preserve the new step |

## Implementation Notes

- keep `server/adapters/mcp/session_capabilities.py` as the stable facade, but
  implement the real state/policy changes in the split session-capability
  modules
- add one explicit creature refinement step such as `refine_low_poly_forms`
  rather than overloading `place_secondary_parts` or `finish_or_stop`
- update `GuidedFlowStepLiteral` in
  `server/adapters/mcp/contracts/guided_flow.py` while keeping the current
  `GuidedFlowFamilyLiteral` vocabulary intact, then wire the real step
  advancement paths in
  `server/adapters/mcp/session_capabilities_registry.py`, especially
  `_maybe_advance_guided_flow_from_part_registry_dict(...)` and the
  checkpoint-outcome transitions that currently move creature work from
  `place_secondary_parts` toward `checkpoint_iterate`
- the current registry helper does not receive `active_gate_plan`; this leaf
  must explicitly choose one owner path:
  - pass a typed gate-blocker summary from `session_capabilities_flow.py` /
    `session_capabilities_runtime_glue.py` into the registry helper
  - or keep role-only advancement in the registry and perform the blocker-aware
    refinement transition in the caller that already owns session gate state
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
gate_state = session.active_gate_plan
role_summary = build_role_summary(domain_profile, current_step, part_registry)
required_roles_ready = all_required_primary_and_secondary_roles_complete(role_summary)
blocking_seams = required_gate_blockers(
    gate_state,
    gate_types={"attachment_seam", "support_contact"},
)
scene_state_clean = not session.spatial_state_stale and not session.spatial_refresh_required

if domain_profile == "creature" and current_step == "place_secondary_parts":
    if required_roles_ready and not blocking_seams and scene_state_clean:
        completed_steps.add("place_secondary_parts")
        current_step = "refine_low_poly_forms"
    else:
        current_step = "checkpoint_iterate" or "inspect_validate"
        next_actions = ["refresh_spatial_context", "run_checkpoint_iterate"]

if current_step == "refine_low_poly_forms":
    guided_allowed_families = [
        "secondary_parts",
        "attachment_alignment",
        "reference_context",
    ]
    # Do not add "primary_masses" just to reuse modeling_transform_object
    # unless TASK-135-03-02-01 deliberately remaps/allows that tool and proves
    # modeling_create_primitive / scene_create stay hidden or blocked.
    planner_selected_family = "modeling_mesh"
    planner_blocked_families = ["sculpt_region"]
    visible_tools = visible_tools_for_gate_plan(active_gate_plan) | refinement_safe_tools
    persist_session_state(current_step, completed_steps, active_gate_plan)
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

| Test File | Cases / Assertions |
|-----------|--------------------|
| `tests/unit/adapters/mcp/test_guided_flow_state_contract.py` | `refine_low_poly_forms` validates in `GuidedFlowStepLiteral`, round-trips through session state, and appears in completed-step ordering only after prerequisite gates clear |
| `tests/unit/adapters/mcp/test_guided_flow_state_contract.py` | stale spatial state or unresolved required seam keeps the flow in `checkpoint_iterate` / `inspect_validate`, not refinement |
| `tests/unit/adapters/mcp/test_visibility_policy.py` | refinement step exposes bounded mesh/modeling/search tools, while broad sculpt remains hidden without explicit `TASK-145` handoff |
| `tests/unit/adapters/mcp/test_guided_mode.py` and `test_guided_surface_benchmarks.py` | guided-mode diagnostics and benchmark-visible tools stay aligned with the new step |
| `tests/unit/adapters/mcp/test_reference_images.py` | checkpoint and iterate responses project the same refinement step/blocker state into `guided_flow_state`, `active_gate_plan`, `refinement_route`, and `refinement_handoff` |
| `tests/unit/adapters/mcp/test_public_surface_docs.py` | public prompt/MCP docs mention the new step only after runtime behavior ships |
| `tests/e2e/integration/test_guided_gate_state_transport.py` | stdio/Streamable payloads carry identical `guided_flow_state.current_step` and gate blockers |
| `tests/e2e/vision/test_reference_stage_truth_handoff.py` | primitive-only low-poly creature with stable parts but unprofiled forms reaches refinement blockers, not final completion |

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
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_router_elicitation.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_guided_surface_benchmarks.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_stage_truth_handoff.py -q`
- `Outside sandbox before closeout: PYTHONPATH=. poetry run pytest ./tests/unit`
- `Outside sandbox for Blender-backed runtime proof: poetry run python scripts/run_e2e_tests.py`

## Status / Board Update

- When this leaf ships, update its task status plus the parent `TASK-135-03`
  execution structure and note whether the umbrella `TASK-135` sequencing text
  also changed.
- Record whether the `pre-commit` lane, owner-lane pytest commands, full unit
  pass, and full Blender E2E pass ran or were intentionally skipped.
- If the explicit refinement step still leaves follow-on runtime or visibility
  work, capture that as a new leaf instead of burying it in the completion
  summary.
