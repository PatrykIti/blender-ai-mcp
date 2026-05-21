# TASK-169: Reference-Guided Quality Drift Regression And Runtime Authority

**Status:** ✅ Done
**Completed:** 2026-05-19
**Priority:** 🔴 High
**Category:** Guided Runtime / Vision / Reconstruction Reliability
**Estimated Effort:** Large
**Follow-on After:** [TASK-135](./TASK-135_Anatomy_Aware_Reference_Guided_Low_Poly_Creature_Reconstruction.md), [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md), [TASK-168](./TASK-168_Profile_Bound_Orchestrator_Shielding_Feedback_And_Memory_Containment.md)
**Related:** [TASK-157](./TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md), [TASK-160](./TASK-160_Guided_Client_Feedback_And_Streamable_HTTP_Recovery_UX.md), [TASK-163](./TASK-163_Vision_Orchestrator_Feedback_Strategy_Normalization_And_Optional_Perception_Adapters.md), [TASK-164](./TASK-164_Local_SigLIP2_Reference_Classifier_Sidecar_And_Operator_Scripts.md)

## Objective

Turn the recent low-poly squirrel failure class into one explicit follow-on
runtime family so `llm-guided` creature sessions stop producing gate-progressing
but visually wrong blockouts after reference-guided manual runs.

This umbrella should not assume that the current runtime ignores reference
images. The observed drift is subtler:

- references were attached and read
- reference-understanding did run
- staged compare / iterate did run
- guided gates did progress

But the overall build still collapsed into a poor result because the current
runtime, packet policy, and client contract together allowed the controller to:

- start from `status="no_match"` on a generic creature path
- build after a transient one-reference understanding before the two-reference
  state fully stabilized
- descend into packet-local blocker repair before the whole animal silhouette
  had converged
- treat gate progress as a substitute for global visual quality
- lose reliable viewport verification on a small but common client contract
  drift (`scene_get_viewport(output_mode="IMAGE_PATH")`)

The desired end state is one runtime-owned quality bar where:

- multi-reference creature sessions stabilize before early build decisions are
  trusted
- global silhouette and dominant masses can stay authoritative earlier than
  local blocker packets when the model is still obviously wrong
- reference-driven quality gates and correction focus stay aligned to the
  shipped low-poly creature contract instead of over-valuing local seam
  success
- bounded optional support evidence remains advisory-only but becomes easier to
  leverage when it can materially improve part localization
- controller-side schema drift no longer quietly destroys viewport-based visual
  verification

## Business Problem

The closed `TASK-135`, `TASK-166`, and `TASK-168` families solved real pieces
of the guided/reference problem:

- `TASK-135` raised the creature fidelity and gate contract beyond primitive
  blob completion
- `TASK-166` decomposed staged compare into bounded view/scope packets
- `TASK-168` made guided orchestration fail closed and compact by default

The new squirrel regression shows the remaining gap between those slices:

- the server can be correct about local scope, local blockers, and local gates
  while still being wrong about the overall creature result
- packet-local compare can become too eager when the animal still needs one
  broad silhouette correction pass
- a generic `guided_manual_build` path can be safe without being good enough
  for species-shaped quality
- controller contract drift on a small verification tool can remove a key
  visual proof path even when the guided runtime itself stays healthy

The business failure is therefore not “the model ignored references.” It is
“the runtime let the session optimize the wrong things in the right order.”

## Runtime Drift Anchor

The motivating squirrel run established the following live-code/runtime facts:

- `router_set_goal(...)` returned `status="no_match"` for the squirrel request,
  so the session continued on `guided_manual_build`
- `reference_understanding` first ran with one attached reference, then later
  refreshed with two attached references
- later staged compare / iterate calls did use two references
- packet-local compare narrowed onto blocker slices such as hindlegs, forelegs,
  and finally ears
- the controller tried to treat `eye_pair` as a guided role even though the
  shipped creature surface keeps it gate-only
- `scene_get_viewport(output_mode="IMAGE_PATH")` failed contract validation,
  weakening final visual verification
- the final Blender result still looked like a vertical primitive stack rather
  than the seated squirrel shown by the front/side references

This umbrella uses squirrel as the regression anchor, but the target family is
generic to future common quadruped creature runs.

## Business Outcome

After this umbrella lands:

- multi-reference creature sessions do not begin shaping the build from a stale
  partial-reference understanding state
- staged compare can prefer one broad creature workset or primary-mass packet
  before dropping to local blocker packets when the silhouette is still
  obviously wrong
- the guided creature quality bar blocks “18/20 gates passed” results that are
  still visually implausible at the whole-model level
- reference-part target drift such as `ears` vs `ear_pair` no longer leaves the
  verifier and planner with avoidable semantic gaps
- bounded viewport verification stays resilient to safe client alias drift and
  teaches the canonical contract clearly when a call is not recoverable
- the squirrel regression family becomes a real unit/integration/Blender-backed
  proof lane instead of an operator anecdote

## Non-Goals

- do not build a squirrel-only special case parallel to the generic creature
  path
- do not replace packet-local compare with a monolithic whole-model compare on
  every run
- do not make optional classifier or segmentation sidecars default-on
- do not let optional support evidence become gate authority
- do not reopen the closed `TASK-135`, `TASK-166`, or `TASK-168` umbrellas as
  active parents; this family is a standalone follow-on
- do not widen the guided public surface just to compensate for client drift

## Execution Structure

| Order | Task | Purpose |
|------|------|---------|
| 1 | [TASK-169-01](./TASK-169-01_Guided_Manual_Build_Entry_And_Multi_Reference_Stabilization.md) | Stabilize no-match creature handoff plus same-session multi-reference understanding so early build choices do not rely on a stale one-reference state |
| 2 | [TASK-169-02](./TASK-169-02_Global_First_Creature_Compare_Priority_And_Local_Packet_Escalation.md) | Add a global-first creature compare policy for the early form-finding stages before local blocker packets take over |
| 3 | [TASK-169-03](./TASK-169-03_Creature_Quality_Bar_Gate_Normalization_And_Advisory_Support_Evidence.md) | Align the low-poly creature quality bar, reference-part normalization, and optional support-evidence use so gate progress tracks actual creature readability |
| 4 | [TASK-169-04](./TASK-169-04_Viewport_Verification_Contract_Recovery_And_Client_Alias_Hardening.md) | Recover viewport-based verification from common client drift without widening the public scene contract unsafely |
| 5 | [TASK-169-05](./TASK-169-05_Squirrel_Reference_Guided_Drift_Regression_Pack.md) | Promote the squirrel failure into transcript-state, compare-priority, and Blender-backed regression proof lanes |
| 6 | [TASK-169-06](./TASK-169-06_Docs_Board_Changelog_And_Closeout_Proof.md) | Close the family with docs, board, changelog, and repo-standard proof alignment |

## Repository Touchpoints

| Path / Module | Expected Ownership | Why It Is In Scope |
|---------------|--------------------|--------------------|
| `server/application/tool_handlers/router_handler.py`, `server/router/application/router.py`, `server/adapters/mcp/areas/router.py` | no-match creature handoff and goal-context owners | the squirrel run starts at `status="no_match"` and the current guided manual-build path is shaped here |
| `server/adapters/mcp/session_capabilities_bootstrap.py`, `session_capabilities_state.py`, `session_capabilities_flow.py`, `session_capabilities_runtime_glue.py` | guided session state and readiness owners | multi-reference stabilization, guided step policy, and post-mutation refresh policy live here |
| `server/adapters/mcp/areas/reference_images_runtime.py`, `server/adapters/mcp/areas/reference_understanding.py` | reference attach and RU refresh owners | same-session attach ordering and RU refresh reuse/stability pass through these seams |
| `server/adapters/mcp/areas/reference.py`, `reference_compare_packets.py`, `reference_planner.py`, `reference_feedback.py`, `reference_truth.py` | staged compare/iterate facade, packet policy, planner, feedback, and truth owners | global-vs-local compare selection, packet narrowing, correction focus, and synthesis all converge here |
| `server/adapters/mcp/contracts/reference.py`, `contracts/quality_gates.py`, `transforms/quality_gate_verifier.py`, `vision/reference_gates.py`, `vision/parsing.py` | gate contract and normalization owners | this family needs global-quality guardrails plus stable role/part normalization such as `ears` vs `ear_pair` |
| `server/adapters/mcp/areas/scene.py`, `scene_viewport.py`, `guided_contract.py` | public viewport contract and alias hardening owners | the broken `IMAGE_PATH` verification call and other safe alias recovery belong on these seams |
| `server/adapters/mcp/vision/runtime.py`, `vision/reference_support.py` | optional classifier/segmentation runtime owners | optional support evidence remains advisory-only but may need better integration into the quality-drift family |
| `tests/unit/adapters/mcp/`, `tests/unit/router/`, `tests/e2e/integration/`, `tests/e2e/router/`, `tests/e2e/vision/` | proof lanes | the drift must be pinned in contract, session, compare, and Blender-backed paths |
| `_docs/_PROMPTS/*`, `_docs/_MCP_SERVER/README.md`, `_docs/_VISION/README.md`, `_docs/_TASKS/README.md`, `_docs/_CHANGELOG/*` | canonical docs and governance owners | the task family changes the runtime bar and client expectations, so docs and history must match |

## Test Matrix

| Slice | Primary Validation Lane | Why |
|------|--------------------------|-----|
| guided manual-build entry and multi-reference stabilization | unit router/reference/session lanes plus guided Streamable integration tests | the drift begins at goal + attach sequencing before modeling starts |
| global-first compare priority | unit reference packet/planner lanes plus guided vision/runtime proof | this is where local blocker packets must stop outranking the whole silhouette too early |
| quality bar and gate normalization | unit gate/reference verifier lanes plus creature vision/runtime tests | “gate progress” must stop drifting away from creature readability |
| viewport contract recovery | unit scene/guided-contract/search-surface lanes plus viewport E2E | the final visual proof path must not fail on common safe client drift |
| squirrel regression family | transcript-state integration tests plus Blender-backed squirrel proof | the motivating failure needs a real pinned regression path |

## Acceptance Criteria

- two-reference creature runs no longer make early build decisions from a stale
  one-reference RU state when the session already expects a broader reference
  set
- packet-local compare remains available, but early creature form-finding can
  insist on a broader body/head/tail or whole-workset packet before local limb
  or ear repair dominates the loop
- a creature session cannot present strong gate progress as success when the
  model is still globally unreadable as the referenced animal
- role/part normalization on the current gate/verifier seams closes avoidable
  reference-target drift such as `ears` vs `ear_pair`
- optional segmentation/classifier evidence remains advisory-only and
  non-mandatory
- the public viewport verification path survives safe alias drift or produces a
  clearer canonical correction path
- the squirrel regression family can be reproduced and then proven fixed by
  explicit unit/integration/Blender-backed lanes

## Docs To Update

- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/README.md` and a new `_docs/_CHANGELOG/*` entry when the
  implementation slices close

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_reference_compare_packets.py`
- `tests/unit/adapters/mcp/test_quality_gate_verifier.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/router/application/test_router_handler_parameters.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/router/test_guided_manual_handoff.py`
- one new Blender-backed squirrel proof lane under `tests/e2e/vision/`

## Changelog Impact

- add one `_docs/_CHANGELOG/*` entry when the family closes or when a major
  runtime slice lands

## Completion Summary

- current-state audit confirmed the family had already landed most of its
  runtime contract across the existing guided/reference, gate, support
  evidence, and viewport-alias seams
- this closeout branch finished the remaining gap by adding an explicit
  broad-first creature compare override for early body/head/tail stages plus a
  deterministic Blender-backed squirrel regression proof lane
- prompt docs, vision docs, MCP docs, and test docs now describe the shipped
  primary-mass-first behavior and the repo-owned squirrel proof surface

## Status / Board Update

- `_docs/_TASKS/README.md` moves `TASK-169` from the promoted To Do queue into
  the completed milestones list with completion date `2026-05-19`
- all direct `TASK-169-*` children close with this umbrella
- later standalone follow-on work discovered after the `TASK-169` closeout is
  tracked explicitly under [TASK-170](./TASK-170_Reference_Target_Canonicalization_And_Support_Latency_Stabilization.md)
  and [TASK-171](./TASK-171_Creature_Attachment_First_Build_Contract_And_Structured_Vision_Handoff.md)
  rather than as reopened `TASK-169-*` children

## Validation Commands

- task-doc planning pass:
  - `git diff --check`
  - targeted consistency grep over `TASK-135`, `TASK-163`, `TASK-166`,
    `TASK-168`, prompt docs, and viewport docs
- implementation proof is owned by the execution subtasks below

## Validation Category

- planning / governance task family definition only for this initial doc slice
