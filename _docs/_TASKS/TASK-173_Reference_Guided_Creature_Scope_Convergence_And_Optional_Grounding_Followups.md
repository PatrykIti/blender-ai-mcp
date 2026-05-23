# TASK-173: Reference-Guided Creature Scope Convergence And Optional Grounding Follow-Ups

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Guided Runtime / Vision / Reconstruction Reliability
**Estimated Effort:** Large
**Follow-on After:** [TASK-135](./TASK-135_Anatomy_Aware_Reference_Guided_Low_Poly_Creature_Reconstruction.md), [TASK-171](./TASK-171_Creature_Attachment_First_Build_Contract_And_Structured_Vision_Handoff.md), [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md)
**Related:** [TASK-155](./TASK-155_Guided_Post_Run_Reliability_Followups.md), [TASK-160](./TASK-160_Guided_Client_Feedback_And_Streamable_HTTP_Recovery_UX.md), [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md), [TASK-169](./TASK-169_Reference_Guided_Quality_Drift_Regression_And_Runtime_Authority.md), [TASK-170](./TASK-170_Reference_Target_Canonicalization_And_Support_Latency_Stabilization.md)

## Relationship To Existing Board Items

- `TASK-135` already established the product bar for anatomy-aware low-poly
  creature reconstruction, but the latest real squirrel run proved the shipped
  controller can still satisfy semantic roles while missing that fidelity bar.
- `TASK-171` already shipped attachment-first creature runtime seams, but the
  current session showed the loop can still over-focus on `Body + Head` and
  defer whole-assembly convergence too long.
- `TASK-172` already shipped the optional classifier and localization runtime
  substrate, but the current failure mode proved that “runtime available” is
  not enough; the creature compare/orchestrator path still needs a consumer
  policy that decides when those optional capabilities should actually be used.
- This umbrella is therefore a consumer follow-on for the real guided creature
  loop. It must not reopen the generic provider-runtime substrate on
  `TASK-140-06` or duplicate the already-closed optional-capability transport
  work from `TASK-172`.

## Objective

Fix the real creature-session failure mode where a guided reference build:

- creates the expected semantic part objects
- keeps optional classifier and vision runtime healthy
- but still converges only to a primitive blockout because the active compare
  scope collapses too early, whole-assembly shape evidence loses precedence,
  and optional localization/segmentation never activate when appendage packets
  remain ambiguous.

After this family lands, the guided creature loop should keep the assembled
creature as the default reconstruction target until deterministic or packeted
evidence proves a narrower local repair is the right next step.

## Business Problem

The latest squirrel session produced a visible mismatch between the product goal
and the shipped runtime behavior:

- the reference images describe one recognizable low-poly squirrel with a
  faceted head, seated ears, readable snout, coherent body profile, and a large
  tail
- the generated Blender result stayed at the “named primitives” stage:
  rectangular body mass, cubic head, spike ears, and detached coarse appendages
- the guided session reached `checkpoint_iterate` and later
  `inspect_validate`, but packeted compare narrowed heavily toward `Body + Head`
  while appendage and whole-assembly quality gates stayed stale or failed
- the optional classifier and external vision runtime both answered, yet the
  compare/runtime policy still failed to converge on the whole creature
- the localization sidecar was configured and healthy, but it was not invoked
  during the session even though appendage ambiguity remained unresolved

This is not a “vision is down” failure. It is a loop-control, workset, and
activation-policy failure:

- semantic role completion was treated as a stronger completion signal than
  whole-assembly shape convergence
- broad-first creature compare and active-scope packet arbitration kept
  recurring around `Body + Head` longer than the session could tolerate
- whole-creature gates for ears and legs kept returning `stale` / `failed`
  because the loop did not sustain fresh assembled-scope proof strongly enough
- optional grounding/localization remained dormant even when the active packet
  focus had already become too narrow for the unresolved creature parts

## Business Outcome

After this umbrella lands:

- a creature run cannot “look done” merely because all semantic objects exist;
  whole-assembly shape and packet-local attachment/proportion evidence must also
  converge
- the controller keeps the assembled creature workset active long enough for
  appendages and tail to contribute meaningfully to compare-time decisions
- whole-assembly compare and local packet compare use one explicit arbitration
  contract instead of drifting toward `Body + Head` by inertia
- optional localization/segmentation sidecars can be activated for bounded
  creature packets when the current compare path is clearly missing the part
  ambiguity it needs to resolve
- operator-facing runtime evidence makes it easy to tell whether classifier,
  vision, localization, and segmentation were merely configured or actually used
  in the packet path that drove the final decision

## Non-Goals

- do not make localization, segmentation, or classifier support default-on for
  all sessions
- do not let optional sidecars pass gates or override deterministic scene truth
- do not introduce squirrel-only logic parallel to the generic creature path
- do not reopen the generic provider-capability runtime substrate already owned
  by `TASK-140-06` / `TASK-172`
- do not replace bounded packet compare with a mandatory full-scene heavy pass
- do not weaken `spatial_refresh_required` or visibility gating just to make
  the current failure disappear superficially

## Execution Structure

| Order | Task | Purpose |
|------|------|---------|
| 1 | [TASK-173-01](./TASK-173-01_Assembled_Creature_Workset_Persistence_And_Packet_Scope_Arbitration.md) | Keep the assembled creature workset alive across secondary-part creation and mutate/refresh cycles, and make packet arbitration explicit when broad-vs-local compare compete |
| 2 | [TASK-173-02](./TASK-173-02_Shape_Convergence_Exit_Criteria_And_Inspect_Validate_Escalation.md) | Stop semantic role completion from outranking silhouette and proportion convergence, and repair build-to-inspect escalation rules |
| 3 | [TASK-173-03](./TASK-173-03_Optional_Localization_And_Segmentation_Activation_For_Creature_Packet_Ambiguity.md) | Add one creature-specific consumer policy that decides when the already-shipped optional localization / segmentation seams should actually activate on bounded ambiguous packets |
| 4 | [TASK-173-04](./TASK-173-04_Existing_Squirrel_Proof_Lane_Extension_And_Runtime_Evidence_Surfacing.md) | Extend the existing squirrel proof lane with explicit runtime-evidence surfacing so operators can see which optional sidecars were actually used |

## Repository Touchpoints

| Path / Module | Expected Ownership | Why It Is In Scope |
|---------------|--------------------|--------------------|
| `server/adapters/mcp/session_capabilities_flow.py`, `server/adapters/mcp/session_capabilities_registry.py`, `server/adapters/mcp/session_capabilities_runtime_glue.py`, `server/adapters/mcp/session_capabilities_state.py` | guided workset, step, and refresh owners | the real failure repeatedly collapsed the active workset back to `Body + Head`; this family must repair the owning runtime seams |
| `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_compare_packets.py`, `server/adapters/mcp/areas/reference_feedback.py`, `server/adapters/mcp/areas/reference_planner.py`, `server/adapters/mcp/areas/reference_truth.py` | staged compare/iterate, packet arbitration, compact feedback, planner, and truth owners | whole-assembly vs local packet selection, correction focus, and gate freshness all converge here |
| `server/adapters/mcp/areas/reference_understanding.py`, `server/adapters/mcp/vision/reference_support.py`, `server/adapters/mcp/vision/runtime.py`, `server/adapters/mcp/vision/backends.py`, `server/adapters/mcp/vision/config.py` | RU, optional sidecar activation, and runtime evidence owners | classifier/localization/segmentation already exist as optional seams; this family decides when they should matter for creature compare packets |
| `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/contracts/quality_gates.py`, `server/adapters/mcp/transforms/quality_gate_verifier.py` | public compare/gate contracts | stale vs failed vs passed gate projection and compare-time capability evidence must stay typed and deterministic |
| `tests/unit/adapters/mcp/`, `tests/unit/router/application/`, `tests/e2e/vision/`, `tests/e2e/integration/`, `scripts/vision_harness.py`, `_docs/_TEST_IMAGES/` | proof lanes and harness owners | the bug came from a real end-to-end guided creature session, so the fix must prove the same class of run with repo-owned squirrel references and typed runtime evidence |
| `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`, `_docs/_VISION/README.md`, `_docs/_MCP_SERVER/README.md`, `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`, `_docs/_PROMPTS/GUIDED_SESSION_START.md`, `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md` | canonical docs | docs must explain the repaired creature loop, optional grounding activation, and sidecar evidence posture |

## Test Matrix

| Slice | Primary Validation Lane | Why |
|------|--------------------------|-----|
| assembled workset persistence and packet arbitration | `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/vision/test_reference_guided_squirrel_quality_regression.py` | the latest failure repeatedly collapsed compare state back to `Body + Head` |
| shape-convergence exit criteria and inspect escalation | `test_quality_gate_verifier.py`, `test_reference_compare_packets.py`, `test_guided_flow_state_contract.py`, `tests/e2e/integration/test_guided_inspect_validate_handoff.py` | semantic role completion must stop outranking shape/profile convergence |
| optional localization/segmentation activation | `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_vision_runtime_config.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/unit/router/application/test_router_contracts.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/vision/test_reference_guided_squirrel_quality_regression.py` | the runtime was healthy, but the creature path never invoked localization during the failing run |
| runtime evidence surfacing and squirrel proof-lane extension | `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/unit/adapters/mcp/test_public_surface_docs.py`, `tests/unit/router/application/test_router_contracts.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/vision/test_reference_guided_squirrel_quality_regression.py`, `scripts/vision_harness.py` | the repo already has a squirrel proof lane; this family must extend it so operators can also see which optional runtimes actually participated |

## Acceptance Criteria

- the active creature workset no longer collapses back to `Body + Head` by
  default after secondary-part creation or bounded attachment repairs unless a
  later packet contract explicitly chooses that narrower scope
- `reference_compare_stage_checkpoint(...)` and
  `reference_iterate_stage_checkpoint(...)` use one explicit arbitration rule
  for broad assembled-scope compare vs local packet compare
- semantic role completion cannot by itself move a creature run into
  `inspect_validate` while whole-assembly shape/profile drift is still the main
  unresolved blocker
- optional localization and segmentation can be invoked on bounded creature
  packets when appendage ambiguity remains unresolved and the current packet
  family is clearly under-grounded
- operator-facing feedback and/or harness artifacts make it clear whether the
  classifier, vision runtime, localization sidecar, and segmentation sidecar
  were merely configured or actually used in the session

## Docs To Update

- `_docs/_TASKS/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_TESTS/README.md`

## Tests To Add/Update

- split across the execution slices below; each child task owns its exact lane

## Changelog Impact

- add one `_docs/_CHANGELOG/*` entry when the first implementation slice lands
- do not treat this planning-only task creation as the changelog event

## Status / Board Update

- `_docs/_TASKS/README.md` should track `TASK-173` as a promoted open item on
  the Vision / Hybrid Loop lane
- child tasks stay nested under the open umbrella and do not need board rows
  unless one later becomes a separately promoted follow-on

## Validation Commands

- `git diff --check`
- `rg -n "TASK-173|Reference-Guided Creature Scope Convergence And Optional Grounding Follow-Ups|Assembled Creature Workset Persistence|Shape Convergence Exit Criteria|Optional Localization And Segmentation Activation|Real Squirrel Proof Lane" _docs/_TASKS/README.md _docs/_TASKS/TASK-173*.md`

## Validation Category

- planning / governance / failure-driven task-family definition
