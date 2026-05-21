# TASK-171: Creature Attachment-First Build Contract And Structured Vision Handoff

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Guided Runtime / Vision / Reconstruction Reliability
**Estimated Effort:** Large
**Follow-on After:** [TASK-169](./TASK-169_Reference_Guided_Quality_Drift_Regression_And_Runtime_Authority.md), [TASK-170](./TASK-170_Reference_Target_Canonicalization_And_Support_Latency_Stabilization.md)
**Related:** [TASK-135](./TASK-135_Anatomy_Aware_Reference_Guided_Low_Poly_Creature_Reconstruction.md), [TASK-157](./TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md), [TASK-163](./TASK-163_Vision_Orchestrator_Feedback_Strategy_Normalization_And_Optional_Perception_Adapters.md), [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md), [TASK-168](./TASK-168_Profile_Bound_Orchestrator_Shielding_Feedback_And_Memory_Containment.md)

## Objective

Turn the next squirrel/common-quadruped follow-on into one explicit runtime and
RU contract family where:

- creature stage advancement is attachment-aware instead of loosely role-count
  driven
- buildable missing-part blockers do not fall into `inspect_validate` before
  the runtime has exhausted the bounded build path
- `guided_register_part(...)` widens the active workset so the next omitted
  compare/iterate pass can see the newly added part
- broad-first compare remains available for unresolved body/head/tail form, but
  it stops suppressing newly registered secondary-part seam/contact repair for
  too long
- compact `reference_orchestrator_feedback` can surface one bounded repair plan
  instead of only flattened tool-name lists and prose focus strings
- reference understanding can hand off a richer creature assembly recipe than
  the current `required_parts` + `construction_strategy` minimum, while staying
  typed, strict, and advisory-only

This is not a prompt-only cleanup. The code audit for this task confirmed that
the remaining drift lives in shipped runtime and contract seams.

## Business Problem

The current guided/reference creature loop already has real structure from
`TASK-163`, `TASK-168`, `TASK-169`, and `TASK-170`:

- typed guided flow state
- fail-closed role/family gating
- packeted compare/iterate
- deterministic seam/contact truth
- compact orchestrator feedback
- canonical creature target labels on the RU path

The remaining squirrel failure class is subtler than “the model ignored the
prompt.” The shipped runtime still has a few contract mismatches that can push
the controller into the wrong loop:

- the high-level creature stage order already exists on prompt and allowed-role
  surfaces, but the stage-exit and build-hold rules still allow late
  carry-forward of `tail_mass` / `snout_mass` and do not align cleanly with the
  required gate set
- `eye_pair` is intentionally gate-only rather than a guided role, but the
  compact iterate loop can still escalate to `inspect_validate` too early
  because gate-only buildable blockers do not participate in `missing_roles`
- `guided_register_part(...)` updates the role registry but does not widen
  `active_target_scope`, so the next omitted-target compare/iterate pass can
  keep looking at a stale workset
- early `place_secondary_parts` compare still prefers the primary-mass workset
  while registered secondary-part seam/contact issues may already need local
  attention
- required creature seam detection still leans heavily on lexical object-name
  heuristics instead of registry-backed creature roles
- compact feedback knows something is wrong, but it usually drops the top
  bounded repair candidate with `arguments_hint`
- RU is already richer than `required_parts` alone, but it still lacks
  attachment-first creature assembly fields that would let the runtime and
  controller agree on anchors, seating order, and contact expectations earlier

## Business Outcome

After this family lands:

- `tail_mass` can no longer quietly carry forward past the primary-wave exit
  path and `snout_mass` can no longer quietly carry forward past the
  secondary-wave exit path without one explicit contract decision reflected in
  runtime, docs, and tests
- gate-only but buildable blockers such as `eye_pair` can keep the session in a
  bounded build lane until hard truth blockers, seam/support failures, or
  stagnation justify `inspect_validate`
- newly registered creature parts join the active workset fast enough that the
  next compare/iterate pass can reason over the actual current assembly
- broad-first compare still protects early silhouette formation, but registered
  secondary-part blocker/focus evidence can override it sooner when the current
  failure is already local
- required creature seams and attachment-pair matching remain deterministic, but
  they no longer depend entirely on helpful object names
- compact feedback can tell the controller which bounded repair tool to call
  next and with what typed argument hints
- RU can surface creature assembly structure such as mass recipes, attachment
  intent, contact expectations, and stage-order seating constraints without
  becoming scene truth or tool-unlock authority

## Non-Goals

- do not reopen classifier / SigLIP2 scope as the main subject of this family
- do not make segmentation or classifier support default-on
- do not create a new public `reference_understand(...)` or
  `router_apply_reference_strategy(...)` tool
- do not let RU become truth authority for seams, stage completion, or tool
  visibility
- do not make `eye_pair` a guided role unless a separate explicit public
  surface decision is made
- do not build squirrel-only special cases parallel to the generic creature
  path
- do not replace the bounded packet system with whole-scene compare by default

## Execution Structure

| Order | Task | Purpose |
|------|------|---------|
| 1 | [TASK-171-01](./TASK-171-01_Buildable_Gate_Escalation_And_Stage_Prerequisite_Repair.md) | Align stage advancement and iterate escalation so `tail_mass`, `snout_mass`, and gate-only buildable blockers obey one explicit runtime contract |
| 2 | [TASK-171-02](./TASK-171-02_Active_Workset_Expansion_And_Secondary_Compare_Precedence.md) | Expand the active workset after `guided_register_part(...)` and let registered secondary-part blocker/focus evidence outrank broad-first compare earlier |
| 3 | [TASK-171-03](./TASK-171-03_Registry_Backed_Creature_Seam_Authority_And_Opaque_Naming.md) | Move required creature seam inference and gate matching toward registry-backed roles with opaque-name fallback coverage |
| 4 | [TASK-171-04](./TASK-171-04_Compact_Repair_Plan_Projection_On_Reference_Orchestrator_Feedback.md) | Add one bounded actionable repair-plan surface to compact feedback without dumping full truth/planner payloads |
| 5 | [TASK-171-05](./TASK-171-05_Attachment_First_Creature_Reference_Understanding_Contract_Expansion.md) | Expand RU with typed creature assembly fields that remain advisory-only and strict-schema validated |
| 6 | [TASK-171-06](./TASK-171-06_Squirrel_Regression_Proof_Docs_And_Closeout.md) | Close the family with live registration/regression coverage, prompt/docs alignment, and board/changelog sync |

## Repository Touchpoints

| Path / Module | Expected Ownership | Why It Is In Scope |
|---------------|--------------------|--------------------|
| `server/adapters/mcp/session_capabilities_flow.py`, `server/adapters/mcp/session_capabilities_registry.py`, `server/adapters/mcp/session_capabilities_runtime_glue.py` | guided stage, role-summary, and active-scope owners | stage prerequisites, part registration, stale workset widening, and spatial refresh/rebind rules live here |
| `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_feedback.py`, `server/adapters/mcp/areas/reference_truth.py`, `server/adapters/mcp/areas/reference_planner.py`, `server/adapters/mcp/areas/reference_images_runtime.py` | compare/iterate, compact feedback, truth, repair-planner, and transport owners | iterate escalation, compare precedence, bounded repair-plan projection, truth-derived seam candidates, and feedback transport projection all converge here |
| `server/application/services/spatial_graph.py` | deterministic creature seam owner | required creature seams still classify head/body/snout/tail/limb mostly from object names here |
| `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/contracts/quality_gates.py`, `server/adapters/mcp/transforms/quality_gate_verifier.py` | typed contracts and gate/verifier owners | buildable gate blockers, compact feedback shape, and registry-backed gate/seam matching belong on these seams |
| `server/adapters/mcp/areas/reference_understanding.py`, `server/adapters/mcp/areas/reference_images_runtime.py`, `server/adapters/mcp/areas/router.py`, `server/adapters/mcp/session_capabilities_state.py`, `server/adapters/mcp/vision/prompting.py`, `server/adapters/mcp/vision/parsing.py`, `server/adapters/mcp/vision/reference_support.py` | RU runtime, transport, session-state, prompt/schema, parser, and support owners | the new attachment-first handoff fields must be added end to end under the existing strict RU contract and stay aligned across persistence plus transport projection |
| `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`, `_docs/_PROMPTS/GUIDED_SESSION_START.md`, `_docs/_MCP_SERVER/README.md`, `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md` | canonical prompt/runtime docs | the public controller guidance must match the new runtime contract and RU vocabulary |
| `tests/unit/adapters/mcp/`, `tests/unit/tools/scene/`, `tests/e2e/integration/`, `tests/e2e/vision/` | proof lanes | this family changes stage flow, scope, gate semantics, seam inference, compact feedback, and RU payload shape |

## Test Matrix

| Slice | Primary Validation Lane | Why |
|------|--------------------------|-----|
| stage prerequisite and buildable gate escalation repair | `test_guided_flow_state_contract.py`, `test_context_bridge.py`, `test_visibility_policy.py`, `test_reference_images.py`, `tests/e2e/integration/test_guided_gate_state_transport.py` | stage advancement and build-vs-inspect policy live on guided session/runtime seams |
| active workset expansion and secondary compare precedence | `test_guided_flow_state_contract.py`, `test_reference_images.py`, `tests/e2e/vision/test_reference_guided_squirrel_quality_regression.py` | omitted-target compare must start seeing newly registered parts and secondary blocker/focus state |
| registry-backed seam authority | `test_quality_gate_verifier.py`, `test_spatial_graph_service.py`, `tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py` | deterministic seam generation must keep working even when lexical names are weak |
| compact repair-plan feedback | `test_contract_payload_parity.py`, `test_guided_gate_state_transport.py`, `tests/e2e/integration/test_guided_inspect_validate_handoff.py`, `tests/e2e/vision/test_reference_stage_truth_handoff.py` | compact feedback is client-facing and must remain typed, bounded, actionable, and correctly transported |
| RU contract expansion | `test_guided_flow_state_contract.py`, `test_vision_prompting.py`, `test_vision_parsing.py`, `test_reference_images.py`, `test_guided_gate_state_transport.py`, `test_reference_understanding_runtime_surface.py` | the RU path is strict-schema validated, session-persisted, and transported on existing public seams |
| closeout regression bundle | repo-standard targeted owner lanes plus the Blender-backed squirrel flow | this family must prove the live registration and attachment-first follow-on, not only unit-level wording |

## Acceptance Criteria

- `tail_mass` stage ownership is explicit and consistent across the guided flow,
  creature prompt docs, and creature gate contract
- `snout_mass` stage ownership is explicit and consistent across the guided
  flow, creature prompt docs, and creature gate contract
- buildable gate-only blockers such as `eye_pair` do not escalate to
  `inspect_validate` until the runtime reaches a hard seam/support/truth
  blocker, repeated stagnation, or another explicitly documented escalation
  boundary
- `guided_register_part(...)` can widen or rebind the active workset safely
  enough that omitted-target compare/iterate sees the newly registered part in
  the same guided loop
- broad-first creature compare remains bounded and available, but registered
  secondary-part blocker/focus evidence can take local precedence before the
  loop finishes every remaining primary-mass-centric pass
- required creature seam inference and attachment-pair matching can use
  registry-backed roles, with lexical-name heuristics only as fallback
- compact `reference_orchestrator_feedback` can expose one bounded actionable
  repair-plan surface with tool and `arguments_hint`
- RU can expose attachment-first typed creature assembly hints while remaining
  strict-schema validated, advisory-only, and on the existing public seams

## Docs To Update

- `_docs/_TASKS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_VISION/README.md`
- `_docs/_CHANGELOG/README.md` and one new `_docs/_CHANGELOG/*` entry when implementation slices land

## Tests To Add/Update

- proof ownership is split across the execution slices below

## Changelog Impact

- add one `_docs/_CHANGELOG/*` entry when the first implementation slice lands
- update the same historical entry or add follow-on entries as the family
  closes, depending on branch size and landing cadence

## Status / Board Update

- `_docs/_TASKS/README.md` adds `TASK-171` to the promoted To Do queue under
  `Vision & Hybrid Loop`
- this umbrella is intentionally standalone follow-on work after the now-closed
  `TASK-169` and `TASK-170` slices; it is not an open child under those closed
  parents

## Validation Commands

- `git diff --check`
- `rg -n "TASK-171|TASK-171-0[1-6]|Creature Attachment-First Build Contract And Structured Vision Handoff|guided_register_part|recommended_repair|anchor_role_candidates" _docs/_TASKS/README.md _docs/_TASKS/TASK-171*.md`

## Validation Category

- planning / governance task family definition only for this initial doc slice
