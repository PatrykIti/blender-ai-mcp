# TASK-135-03: Low-Poly Form Refinement Mesh Window And Profile Macros

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-135](./TASK-135_Anatomy_Aware_Reference_Guided_Low_Poly_Creature_Reconstruction.md)
**Category:** Reconstruction / Guided Mesh Refinement
**Estimated Effort:** Large
**Depends On:** [TASK-157](./TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md), [TASK-135-01](./TASK-135-01_Creature_Blockout_Completion_Contract_And_Required_Detail_Gates.md)

## Objective

Add a stage-gated low-poly form refinement path after primitive mass placement,
so guided creature sessions can move beyond "geometric blobs placed near each
other" while still staying bounded and LLM-safe.

The goal is not photoreal sculpting. The goal is a recognizable low-poly
creature profile:

- tapered or flattened body masses where the reference requires it
- seated limbs instead of separate balls
- pointed or wedge-like ears
- small eyes/nose/snout details
- shaped tail segments
- visibly attached parts

## Business Problem

The current creature recipe exposes modeling and mesh tools, but the flow can
still behave as though primitive placement is the whole product. That creates
results that technically contain the requested object names, but still look like
unrefined spheres/ellipsoids.

For low-poly reconstruction, the expected baseline should be:

- primary masses first
- attachment/seam repair
- then a bounded mesh/modeling refinement window
- then final checkpoint

Without an explicit refinement window, clients often stop too early or avoid
mesh tools entirely.

This file is now a technical subtask and decomposition anchor. Do not execute
it as one oversized leaf; use the dedicated `TASK-135-03-*` leaves below.

The staged checkpoint loop already emits `refinement_route` and
`refinement_handoff` from `TASK-145`. This subtask must wire an explicit
creature refinement step into that existing planner/checkpoint baseline instead
of creating a second refinement recommendation path.

## Repository Touchpoints

| Path / Module | Expected Change |
|---------------|-----------------|
| `server/adapters/mcp/session_capabilities.py` | Keep the public session-capability facade stable while refinement-stage state routes through the split modules below |
| `server/adapters/mcp/contracts/guided_flow.py` | Add the explicit refinement step literal and keep the existing guided family vocabulary strict on public router/reference payloads |
| `server/adapters/mcp/session_capabilities_registry.py` | Advance into and out of the refinement step from role registration and checkpoint outcomes on the current split guided runtime |
| `server/adapters/mcp/session_capabilities_state.py` | Persist the updated guided flow state, gate plan, and stale markers for the refinement step in the canonical session state |
| `server/adapters/mcp/session_capabilities_flow.py` | Extend creature step sequencing and role-group policy for the refinement stage |
| `server/adapters/mcp/session_capabilities_runtime_glue.py` | Keep gate-plan refresh, stale marking, and visibility sync aligned with the new refinement stage |
| `server/adapters/mcp/transforms/visibility_policy.py` | Open bounded mesh/modeling tools only when refinement prerequisites pass |
| `server/adapters/mcp/discovery/search_documents.py` and `server/adapters/mcp/discovery/search_surface.py` | Add low-poly profile/refinement search cues on the live discovery surface |
| `server/adapters/mcp/areas/reference.py` | Keep the public staged compare/iterate surface aligned while the split planner/feedback owners below project refinement details |
| `server/adapters/mcp/areas/reference_planner.py` | Keep `refinement_route` / `refinement_handoff` aligned with the explicit refinement step and current candidate ranking logic |
| `server/adapters/mcp/areas/reference_feedback.py` | Keep `reference_orchestrator_feedback` aligned when refinement changes selected family, blockers, next actions, or checkpoint advice |
| `server/adapters/mcp/areas/mesh.py` | Ensure selected mesh tools work in the guided refinement window |
| `server/adapters/mcp/areas/modeling.py` | Keep bounded transforms available for part profiling |
| `server/adapters/mcp/areas/scene.py` | Add or expose profile macros if needed |
| `server/router/infrastructure/tools_metadata/` | Add gate metadata for refinement tools and macros |
| `server/application/tool_handlers/macro_handler.py` | Add optional profile macros only when existing mesh tools are insufficient |
| `blender_addon/application/handlers/mesh.py` | Update if new mesh operations are required |
| `blender_addon/application/handlers/modeling.py` | Update if profile macros need addon support |
| `tests/unit/adapters/mcp/` | Visibility, checkpoint, gate prerequisite tests |
| `tests/unit/tools/macro/` | Profile macro tests if macros are introduced |
| `tests/e2e/tools/mesh/` | Blender-backed mesh refinement tests |
| `tests/unit/adapters/mcp/test_reference_images.py` | Keep low-poly refinement-family routing aligned with the checkpoint planner surfaces |
| `tests/e2e/vision/test_reference_stage_truth_handoff.py` | Prove the staged refinement route/handoff stays aligned with the explicit refinement step |
| `tests/e2e/vision/` | Primitive-only creature cannot complete before refinement gate |
| `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md` | Document refinement window and completion blockers |
| `_docs/_MCP_SERVER/README.md` | Document gated mesh visibility and profile gate semantics |

## Implementation Notes

- Add an explicit guided creature step such as `refine_low_poly_forms` after
  required masses and seams are stable enough.
- Keep the visible tool window narrow and role-aware:
  - `mesh_select`
  - `mesh_select_targeted`
  - `mesh_extrude_region`
  - `mesh_loop_cut`
  - `mesh_bevel`
  - `mesh_symmetrize`
  - bounded modeling transforms
  - selected creature macros
- Do not unlock broad sculpt by default for this stage.
- Prefer reusable bounded macros only when repeated primitive-to-form
  refinement cannot be expressed safely enough with the bounded mesh/modeling
  window.
- Extend the existing `refinement_route` / `refinement_handoff` baseline from
  `TASK-145` and the current checkpoint assembler in
  `server/adapters/mcp/areas/reference.py`; do not build a second refinement
  planner beside those shipped surfaces.
- Keep the two vocabularies separate:
  - `guided_flow_state.allowed_families` stays on the current
    `GuidedFlowFamilyLiteral` values from
    `server/adapters/mcp/contracts/guided_flow.py`
  - planner-facing families such as `macro`, `modeling_mesh`, or
    `sculpt_region` stay on the checkpoint-local `refinement_route` /
    `reference_strategy_state` contracts from
    `server/adapters/mcp/contracts/reference.py`
- Treat candidate names such as `macro_refine_creature_part_profile`,
  `macro_point_creature_ears`, `macro_flatten_limb_contact_patch`, and
  `macro_add_creature_eye_pair` as optional follow-ons, not as already-shipped
  tools.
- Add relation-aware preconditions:
  - do not refine final form while required seams still float
- do not use mesh edits to hide unresolved attachment failures
- do not call the model complete immediately after primitive creation
- Model refinement as a generic `refinement_stage` gate with creature-specific
  `shape_profile` child gates for body, ears, limbs, snout, and tail where
  normalized gate evidence and verifier-supported support refs require them.
- Consume `TASK-157` evidence refs rather than calling perception directly:
  `reference_understanding` may explain that the target is a faceted
  squirrel-like creature with wedge ears and a curled tail, while
  `silhouette_analysis` or future segmentation masks may support active
  `shape_profile` gates. The refinement stage still opens bounded mesh/modeling
  tools only after gate prerequisites pass.
- Keep the closed-owner split explicit: bounded RU summary/linkage and
  default-off optional support-evidence adapters already ship on the closed
  `TASK-163` seams. This refinement task consumes those support refs through the
  closed `TASK-157` substrate and must not reopen earlier closed
  vision-planning owners.
- Keep broad sculpt out of the default low-poly refinement path. Sculpt remains
  a planner-driven, preconditioned handoff from `TASK-145`, not the baseline
  answer for faceted low-poly profile work.

## Pseudocode

```python
if current_step == "place_secondary_parts" and required_roles_complete:
    if required_seams_stable:
        advance_to("refine_low_poly_forms")

if current_step == "refine_low_poly_forms":
    guided_allowed_families = [
        "secondary_parts",
        "attachment_alignment",
        "reference_context",
    ]
    planner_allowed_families = ["modeling_mesh", "macro"]
    visible_tool_targets = [
        "mesh_select",
        "mesh_select_targeted",
        "mesh_extrude_region",
        "mesh_loop_cut",
        "mesh_bevel",
        "mesh_symmetrize",
        # Optional profile macros may join later if bounded mesh/modeling tools
        # are not sufficient for the first slice.
    ]
```

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-135-03-01](./TASK-135-03-01_Refinement_Stage_State_And_Visibility_Gate.md) | Add the explicit refinement stage to guided state, gate policy, and visibility shaping |
| 2 | [TASK-135-03-02](./TASK-135-03-02_Bounded_Profile_Tools_And_Optional_Macro_Wave.md) | Make the refinement stage operational with bounded profile tools and only the smallest necessary macro additions |
| 3 | [TASK-135-03-03](./TASK-135-03-03_Refinement_Regression_Docs_And_Closeout.md) | Lock the new refinement path with transport/Blender-backed proof and final docs/changelog alignment |

## Runtime / Security Contract Notes

- Visibility level: keep refinement on the existing public `guided_flow_state`,
  `active_gate_plan`, `reference_images(...)`, and staged checkpoint surfaces.
  Do not add a new public refinement tool or a second creature-only flow.
- Read-only vs mutating behavior: refinement-step state, blockers, route, and
  handoff remain server/session-state outputs. Existing modeling, mesh, scene,
  and macro tools remain the only mutating Blender paths and must mark affected
  refinement evidence stale after scene changes.
- Mode and selection impact: refinement tools may temporarily enter edit mode,
  but the step must preserve or explicitly restore expected mode and selection
  through the existing guided runtime helpers before returning.
- Session and auth assumptions: refinement-step progression stays scoped to the
  active stdio or Streamable HTTP session, with local Blender RPC as the only
  trusted mutating backend.
- Parameter validation and compatibility: new step names, family literals,
  checkpoint fields, and any profile-macro arguments use strict typed contracts
  with reject-unknown behavior. Compatibility shims stay explicit in the owning
  contract layer.
- Side effects, recovery, and logging: treat
  `reference_understanding_summary`, `part_segmentation`, and silhouette
  signals as support evidence only; classifier or segmentation details stay
  nested inside the existing RU / part-segmentation surfaces rather than
  becoming new top-level refinement contracts. The verifier still owns gate
  pass/fail. If prerequisites are stale or unresolved, return blockers or
  `inspect_validate` rather than a docs-only refinement notion. Keep provider
  keys, local paths, and raw vision debug payloads out of logs.
- Resource and timeout limits: keep the first refinement window bounded to the
  current assembled creature scope or a small active object set already selected
  by the checkpoint loop, and avoid unbounded repeated mesh passes from one
  checkpoint result before the next staged refresh.
- Sculpt boundary: keep sculpt hidden on the normal refinement stage unless a
  later bounded `TASK-145` handoff explicitly recommends it.

## Tests To Add/Update

| Layer | Tests |
|-------|-------|
| Unit guided state | `refine_low_poly_forms` appears only after required roles/seams are stable |
| Unit visibility | Mesh tools open for refinement gate and remain hidden before prerequisites |
| Unit search | "profile low-poly body/ears/limbs" returns bounded mesh/profile tools |
| Unit safety | Sculpt remains hidden unless planner emits explicit sculpt handoff |
| Unit checkpoint | Primitive-only creature reports refinement blockers |
| Unit evidence refs | `TASK-157` plus the shipped `TASK-163` support refs for shape-profile gates open only bounded profile tools after prerequisites |
| Unit guided public surface | Guided family summaries, guided-mode visibility, and public surface docs stay aligned with the new refinement step |
| Unit guided enforcement | Context-bridge and guided execution enforcement stay aligned if refinement or optional macros become visible mutators |
| E2E mesh | A selected part can be profiled through guided mesh tools without losing state |
| E2E vision | Primitive-only squirrel cannot pass final completion before refinement gate |
| E2E macro | Any new profile macro has Blender-backed geometry assertions |
| E2E Streamable guided surface | Guided visibility/search and mutator enforcement stay aligned on the Streamable HTTP path, not only stdio |

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
  `test_public_surface_docs.py` when the explicit refinement stage changes
  guided-surface wording
- `_docs/_CHANGELOG/README.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when the refinement stage or first profile
  macro ships.

## Validation Commands

- `git diff --check`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_guided_surface_benchmarks.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_context_bridge.py -q`
- `poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py tests/e2e/integration/test_guided_streamable_spatial_support.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_goal_derived_gate_creature_completion.py tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py tests/e2e/vision/test_reference_stage_truth_handoff.py -q`
- `Outside sandbox before closeout: PYTHONPATH=. poetry run pytest ./tests/unit`
- `Outside sandbox for Blender-backed runtime proof: poetry run python scripts/run_e2e_tests.py`

## Status / Board Update

- When this refinement parent ships, update its task status plus the child leaf
  statuses under `TASK-135-03`, refresh the umbrella `TASK-135` execution
  structure if ordering or remaining follow-ons changed, and record whether
  `_docs/_TASKS/README.md` board wording also changed.
- Record whether the `pre-commit` lane, owner-lane pytest commands, full unit
  pass, full Blender E2E pass, and any Streamable/stdio parity lanes ran or
  were intentionally skipped.
- If follow-on refinement work remains after the first bounded wave, track it as
  an explicit new leaf or follow-on task instead of burying it in the status
  field.

## Acceptance Criteria

- The guided creature recipe has a clear refinement stage after primitive
  placement and seam stabilization.
- Mesh tools are available when they are actually needed for low-poly form
  refinement, not only hidden behind generic discovery.
- Primitive-only blobs are no longer considered the final expected output for
  a reference-guided creature session.
- The first implementation keeps the surface bounded, role-aware, and
  compatible with existing guided state and visibility policy.
