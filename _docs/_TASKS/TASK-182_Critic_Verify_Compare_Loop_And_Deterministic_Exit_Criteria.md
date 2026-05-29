# TASK-182: Critic/Verify Compare Loop And Deterministic Exit Criteria

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Vision / Loop Control And Verification
**Estimated Effort:** Large
**Follow-on After:** [TASK-173](./TASK-173_Reference_Guided_Creature_Scope_Convergence_And_Optional_Grounding_Followups.md), [TASK-157](./TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md), [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md)
**Related:** [TASK-169](./TASK-169_Reference_Guided_Quality_Drift_Regression_And_Runtime_Authority.md), [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md), [TASK-178](./TASK-178_Structured_Per_Finding_Compare_Schema.md)

## Relationship To Existing Board Items

- `TASK-157` already shipped the deterministic gate verifier and status model
  (`transforms/quality_gate_verifier.py`, `contracts/quality_gates.py`). This
  family does not replace that authority; it makes the compare loop actually
  re-prove each prior defect against that authority before a gate is allowed to
  advance, and formalizes that the non-VLM gate result wins over VLM verdicts.
- `TASK-166` established the hierarchical packet compare substrate
  (`areas/reference_compare_packets.py`) and the two-pass extraction/ranking
  split. This family adds a Critic/Verify dimension on top of that substrate; it
  must reuse the existing `ReferenceComparePacketContract` packet identity and
  diagnostics, not fork a parallel packet model.
- `TASK-169` proved, with the squirrel regression lane, that whole-assembly
  gates can stay `stale`/`failed` while a run advances. This family fixes the
  missing re-render-and-verify step that let that drift slip through.
- `TASK-172` shipped the optional, default-off perception runtime seam
  (localization/segmentation sidecars). This family keeps those sidecars
  advisory and packet-bounded; it does not reopen the `TASK-140-06`
  provider-capability substrate.
- `TASK-173` repaired creature scope convergence and shape-convergence exit
  criteria. This family is the verification-loop complement: where `TASK-173`
  decided *which scope* to keep converging, `TASK-182` decides *whether the
  prior defects in that scope were actually resolved* before advancing.
- This umbrella is therefore a standalone consumer follow-on. It links the
  parents above through **Follow-on After** / **Related**, and its own child
  tasks point at this umbrella via **Parent**.

## Objective

Make the compare loop re-prove its own work and expose one unambiguous,
deterministic-first exit path:

- split compare into a **Critic** pass that emits defects with stable IDs and a
  **Verify** pass that re-renders the *same* views and checks off each open
  defect ID, so a gate only advances when its scope defects are
  verified-resolved or explicitly downgraded
- formalize a **layered exit**: a hard non-VLM gate first (registry part-count
  match AND required contacts via the deterministic verifier), VLM verdict only
  as a tiebreaker, every claim provenance-tagged
- collapse the 4-6 overlapping recommendation/correction channels into one
  ranked `authoritative_next_actions` field so the orchestrating LLM stops
  guessing channel precedence

After this family lands, advancing a scope gate requires deterministic proof
that each previously reported defect was re-checked against the same framing,
and the orchestrator receives a single ranked action list with explicit
provenance instead of parallel, equally-weighted advisory channels.

## Business Problem

The latest guided runs surfaced three concrete, code-level gaps:

- **No re-render verification step.** `build_compare_packets(...)` in
  `areas/reference_compare_packets.py:1016` plans packets and
  `synthesize_packet_vision_result(...)` (`:1258`) merges them, but nothing
  re-renders the same packet views after an edit to confirm a prior defect was
  resolved. `ReferenceComparePacketContract` (`contracts/reference.py:532`)
  has no stable defect identity to check off across cycles, so the squirrel run
  advanced while whole-assembly gates stayed stale.
- **VLM verdicts over-score and drift run-to-run.** Packet
  `correction_focus`/`evidence_summary` arrive as advisory prose with no
  deterministic re-proof, and `compare confidence` is non-authoritative and not
  range-validated. There is no contract that says "this open defect is now
  verified-resolved because the deterministic verifier re-passed", so a
  re-render that *looks* better can read as done.
- **4-6 overlapping recommendation/correction channels.**
  `build_reference_orchestrator_feedback(...)`
  (`areas/reference_feedback.py:384`) already concatenates `next_actions`,
  `recommended_support_tools`, `recommended_repair`, `correction_focus`,
  `evidence_summary`, and `uncertainty_notes` from multiple upstream sources
  (planner blockers, gate completion blockers, packet correction focus, vision
  prose, runtime policy block). `select_refinement_route(...)`
  (`areas/reference_planner.py:623`) adds a parallel family/route channel. The
  precedence between these is implicit, so the orchestrator cannot reliably tell
  which action is the authoritative next step versus advisory context.

These are loop-verification and channel-precedence failures, not "vision is
down" failures. The deterministic verifier in
`transforms/quality_gate_verifier.py:22` already owns authoritative gate truth;
this family makes the compare loop consult it as the hard gate and demotes VLM
output to a tiebreaker with explicit provenance.

## Business Outcome

After this umbrella lands:

- a scope gate cannot advance on a single optimistic re-render; every open
  defect for that scope must be re-checked against the same views and either
  verified-resolved or explicitly downgraded with a recorded reason
- defects carry stable IDs across Critic and Verify cycles, so the orchestrator
  and the proof lanes can see exactly which prior problem each re-render closed
- the exit decision is layered and auditable: the deterministic part-count /
  contact gate is the hard authority, the VLM verdict only breaks ties, and
  every surfaced claim states whether it came from `scene_truth`,
  `mesh_metric`, `spatial_relation`, or advisory `vision`
- the orchestrator receives one ranked `authoritative_next_actions` list with
  provenance instead of 4-6 equally-weighted channels
- vision stays advisory throughout: no Critic/Verify field marks a gate complete
  or unlocks a tool

## Non-Goals

- do not let vision become a truth source. New Critic/Verify and exit fields are
  still VLM interpretation; they must keep `not_truth_source` and
  `requires_deterministic_checks_for_correctness`. Deterministic inspection /
  assertion / silhouette own scene truth; vision must not mark gates complete or
  unlock tools.
- do not emit any magnitude as an authoritative absolute measurement. Any
  size/offset surfaced by Verify must be a proportional ratio versus a trusted
  reference anchor, never a metric absolute (VLMs land within 2x only ~37% of
  the time on metric tasks).
- do not make the heavier perception sidecars (SAM/SAM2/GroundingDINO/
  Depth-Anything/CLIP/DINO embeddings) default-on. They stay default-off,
  advisory-only, and packet-bounded per the `TASK-172` optional-runtime seam,
  and this family does not reopen the `TASK-140-06` provider-capability
  substrate.
- do not emit raw coordinate tokens as primary evidence. Verify findings stay
  symbolic (relation + proportional ratio); coordinates are produced only on
  demand and never as the default packet evidence.
- do not add VLM-side chain-of-thought for spatial judgments. The Critic emits
  defects and the Verify pass reports per-defect resolved/unresolved; all
  reasoning and ranking stays in the orchestrator.
- do not fork the packet model. Reuse `ReferenceComparePacketContract` identity
  and `ReferenceCompareDiagnosticsContract`; do not introduce a parallel compare
  pipeline.

## Execution Structure

| Order | Task | Purpose |
|------|------|---------|
| 1 | [TASK-182-01](./TASK-182-01_Critic_Verify_Split_With_Stable_Defect_Identifiers.md) | Critic/Verify Split With Stable Defect Identifiers |
| 2 | [TASK-182-02](./TASK-182-02_Deterministic_First_Layered_Exit_And_Channel_Consolidation.md) | Deterministic-First Layered Exit And Channel Consolidation |

## Repository Touchpoints

| Path / Module | Expected Ownership | Why It Is In Scope |
|---------------|--------------------|--------------------|
| `server/adapters/mcp/areas/reference_compare_packets.py` | packet planning, packet phase merge, packet synthesis | `build_compare_packets(...)` (`:1016`), `merge_packet_phase_results(...)` (`:1213`), and `synthesize_packet_vision_result(...)` (`:1258`) must gain a Critic pass that emits defect IDs and a Verify pass that re-renders the same views and resolves them |
| `server/adapters/mcp/areas/reference_feedback.py` | compact orchestrator read model | `build_reference_orchestrator_feedback(...)` (`:384`) already merges the overlapping channels; it must project one ranked `authoritative_next_actions` field with provenance instead of parallel lists |
| `server/adapters/mcp/areas/reference_planner.py` | refinement route + correction candidate ranking | `select_refinement_route(...)` (`:623`) and `build_correction_candidates(...)` (`:1194`) are the parallel family/correction channels that must feed the single ranked action field, with provenance preserved |
| `server/adapters/mcp/transforms/quality_gate_verifier.py` | deterministic gate authority | `verify_gate_plan_with_relation_graph(...)` (`:22`) and `_apply_final_completion_status(...)` (`:386`) are the hard non-VLM gate; the layered exit consults this first and treats VLM verdict only as a tiebreaker |
| `server/adapters/mcp/sampling/result_types.py` | typed vision result envelopes | `VisionAssistContract` (`:149`) and `VisionBoundaryPolicyContract` (`:115`) must carry the new defect/verify fields while keeping `not_truth_source` / `requires_deterministic_checks_for_correctness` |
| `server/adapters/mcp/contracts/reference.py` | public compare/feedback contracts | `ReferenceComparePacketContract` (`:532`), `ReferenceCompareDiagnosticsContract` (`:557`), and `ReferenceOrchestratorFeedbackContract` (`:336`) own the stable defect IDs, verify status, and the new ranked action field |
| `tests/unit/adapters/mcp/`, `tests/e2e/integration/`, `tests/e2e/vision/` | proof lanes | the failure came from a real guided run, so the fix must prove defect-ID round-trips, deterministic-first exit, and single-channel action ranking |
| `_docs/_VISION/README.md`, `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`, `_docs/_TASKS/README.md` | canonical docs | docs must describe the Critic/Verify loop, the layered deterministic-first exit, and the consolidated authoritative action channel |

## Test Matrix

| Slice | Primary Validation Lane | Why |
|------|--------------------------|-----|
| Critic/Verify split and stable defect identity | `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/e2e/integration/test_guided_inspect_validate_handoff.py` | defect IDs must survive a Critic -> edit -> Verify round-trip and only check off when the same views are re-rendered |
| deterministic-first layered exit | `tests/unit/adapters/mcp/test_quality_gate_verifier.py`, `tests/e2e/vision/test_goal_derived_gate_creature_completion.py` | the hard non-VLM gate must win; VLM verdict only breaks ties; gate advance must require verified-resolved defects |
| channel consolidation and provenance | `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/e2e/vision/test_goal_derived_gate_creature_completion.py` | the 4-6 overlapping channels must collapse into one ranked `authoritative_next_actions` field with provenance tags |

## Acceptance Criteria

- a Critic pass emits defects with stable IDs that persist across compare
  cycles, and a Verify pass re-renders the *same* views and reports each open
  defect as resolved, unresolved, or explicitly downgraded with a recorded
  reason
- a scope gate advances only when all open defects for that scope are
  verified-resolved or explicitly downgraded; an optimistic single re-render
  with stale open defects does not advance the gate
- the exit decision is layered: `verify_gate_plan_with_relation_graph(...)`
  (registry part-count match AND required contacts) is consulted first as the
  hard gate, and the VLM verdict is used only to break ties between otherwise
  equal deterministic outcomes
- every surfaced compare/feedback claim is provenance-tagged with its source
  class (`scene_truth` / `mesh_metric` / `spatial_relation` / advisory `vision`)
- the orchestrator read model exposes one ranked `authoritative_next_actions`
  field; the previously parallel `next_actions`, `recommended_support_tools`,
  `recommended_repair`, and `correction_focus` channels feed it with preserved
  provenance rather than competing as equals
- vision stays advisory: no new field can mark a gate complete or unlock a tool,
  and `VisionBoundaryPolicyContract` flags remain enforced
- **research caveat:** the cited benchmarks (LL3M one-pass edit rate, IR3D-Bench
  layered metrics, SayPlan replanning) are indoor-scan / synthetic and NOT
  Blender-vs-reference; re-measure absolute gains on
  `tests/fixtures/vision_eval` golden fixtures before promoting any threshold or
  default

## Docs To Update

- `_docs/_TASKS/README.md`
- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_VISION/HYBRID_LOOP_REAL_CREATURE_EVAL.md`

## Tests To Add/Update

- split across the execution slices below; each child task owns its exact lane

## Changelog Impact

- planning-only now; add a `_docs/_CHANGELOG/*` entry when the first slice lands
- do not treat this planning-only task creation as the changelog event

## Status / Board Update

- `_docs/_TASKS/README.md` should track `TASK-182` as a promoted open item on the
  Vision / Hybrid Loop lane
- child tasks stay nested under the open umbrella and do not need board rows
  unless one later becomes a separately promoted follow-on

## Validation Commands

- `git diff --check`
- `rg -n "TASK-182|Critic/Verify Compare Loop And Deterministic Exit Criteria|Critic/Verify Split With Stable Defect Identifiers|Deterministic-First Layered Exit And Channel Consolidation|authoritative_next_actions" _docs/_TASKS/TASK-182*.md`

## Validation Category

- planning / governance / task-family definition
