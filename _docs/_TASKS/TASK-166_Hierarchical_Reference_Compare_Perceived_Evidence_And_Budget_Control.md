# TASK-166: Hierarchical Reference Compare, Perceived Evidence, And Budget Control

**Status:** 🚧 In Progress
**Priority:** 🔴 High
**Category:** Vision / Hybrid Loop / Guided Runtime
**Estimated Effort:** Large
**Follow-on After:** [TASK-145](./TASK-145_Spatial_Repair_Planner_And_Sculpt_Handoff_Context.md), [TASK-163](./TASK-163_Vision_Orchestrator_Feedback_Strategy_Normalization_And_Optional_Perception_Adapters.md), [TASK-140-06](./TASK-140-06_OpenRouter_Model_Capability_Aware_Vision_Runtime.md)
**Related:** [TASK-122-03-06](./TASK-122-03-06_Hybrid_Loop_Model_Aware_Budget_And_Scope_Control.md), [TASK-135](./TASK-135_Anatomy_Aware_Reference_Guided_Low_Poly_Creature_Reconstruction.md), [TASK-136](./TASK-136_Reference_Guided_Architecture_And_Building_Reconstruction.md), [TASK-137](./TASK-137_Anatomy_Aware_Reference_Guided_Organ_Reconstruction.md), [TASK-138](./TASK-138_Anatomy_Aware_Reference_Guided_Biped_And_Fantasy_Character_Reconstruction.md), [TASK-160](./TASK-160_Guided_Client_Feedback_And_Streamable_HTTP_Recovery_UX.md)
**Context Anchor:** [324. TASK-166 packeted stage compare core](../_CHANGELOG/324-2026-05-08-task-166-packeted-stage-compare-core.md)
**Objective:** Replace monolithic staged compare/iterate payloads with a hierarchical packeted compare family, deterministic pre-LLM image evidence, optional heavier perception support, additive packet transparency on the existing staged contracts, and configurable compare budgets that scale from simple to super-complex 6-12 image runs.

## Objective

Replace the current monolithic staged compare/iterate payload strategy with one
hierarchical compare family that:

- decomposes work by view and active scope instead of sending the whole model at
  once
- uses deterministic CV and optional PyTorch-based perception support before
  asking an LLM broad image questions
- scales from:
  - simple models
  - complex assembled models
  - super-complex 6-12 image reference sets
- exposes compare-related input/output budgets as explicit runtime config
  instead of one hard-coded assistant policy

## Business Problem

The current compare/iterate lane mixes too many responsibilities into one
request:

- multiple reference images
- multiple view intents
- full assembled target scope
- broad truth bundles
- visual extraction
- correction ranking
- planner/handoff context

That works for small cases until it does not. Once the request grows:

- vision compare can fail with `input_budget_exceeded`
- multi-image structured output can become parse-fragile
- one failed packet can block a larger iteration even when some views already
  produced useful evidence
- raising `VISION_MAX_TOKENS` can help output size, but it does not solve the
  fixed assistant input budget or the oversized compare shape itself

The core business issue is therefore not "the model needs more tokens". It is
"the compare architecture asks one model call to do too much at once."

## Business Outcome

After this umbrella lands:

- reference compare is decomposed into bounded packets by view and by scope
- deterministic CV extracts low-level image facts before the LLM sees the packet
- optional PyTorch sidecars can enrich packet evidence when justified, without
  becoming authoritative by default
- one short synthesis layer can merge packet results for the LLM/operator
- packet provenance, pass status, conflicts, and budget pressure can surface
  additively on the existing staged compare / iterate contracts when clients
  need more than the compact summary
- compare budgets are configurable and diagnosable at runtime

## Non-Goals

- do not replace deterministic truth with VLM-only authority
- do not make classifier or segmentation sidecars default-on gate authority
- do not widen the default `llm-guided` bootstrap surface with a large new tool
  family
- do not treat larger budgets as the main solution when packet decomposition is
  the real fix
- do not hardcode creature-only heuristics into the generic compare family
- do not create a second planner/evidence flow that duplicates
  `silhouette_analysis`, `part_segmentation`, `planner_detail`,
  `budget_control`, or `reference_orchestrator_feedback`

## Product Design Principles

### 1. View-first compare

- do not compare every view in one payload by default
- front, side, and optional top/silhouette packets should be first-class
  compare units
- view packets should stay individually inspectable and retryable

### 2. Scope-first compare

- do not compare the whole assembled model when only one blocker cluster matters
- packet by active scope such as:
  - `Body + Head`
  - `Tail`
  - `Ears`
  - domain-specific packet groups for larger models

### 3. Truth-first, vision-second

- deterministic tools must establish structural truth first:
  - `scene_scope_graph`
  - `scene_relation_graph`
  - `scene_view_diagnostics`
- vision should answer narrower packet questions on top of that truth
- the LLM should not be asked one giant "what is wrong with the whole model?"
  prompt

### 4. Two-pass compare

- pass 1: bounded visual extraction for the packet
- pass 2: bounded correction ranking and synthesis only when needed
- the second pass should be skippable for clean or low-information packets

### 5. Deterministic CV before broad LLM interpretation

- always-on lightweight CV should pre-chew image facts for the compare family
- optional heavier PyTorch sidecars should be advisory-only enrichers, not the
  default authority
- the LLM should consume compact packet evidence, not raw overloaded image+text
  bundles wherever deterministic extraction is sufficient

## Complexity Tiers

| Tier | Model Shape | Typical Reference Set | Intended Compare Strategy |
|------|-------------|------------------------|---------------------------|
| Simple | one or a few primary masses | 1-2 images | one or two view packets, minimal truth slice, often no synthesis pass |
| Complex | assembled multi-part model | 2-6 images | view-first and scope-first packets plus short synthesis |
| Super-complex | many parts / many views / many references | 6-12 images | packet scheduler, per-packet extraction, bounded synthesis, optional sidecar enrichment |

## Integration With Existing Flow

This family should integrate into the current runtime by **refactoring the
inside** of the existing staged compare tools, not by introducing a second
public compare surface.

### Current Flow Today

The current high-level path is:

1. `reference_images(...)` attaches references and refreshes
   `reference_understanding_summary`.
2. `reference_compare_stage_checkpoint(...)` captures staged views, builds one
   `VisionRequest`, injects one broad `truth_summary`, and calls
   `run_vision_assist(...)`.
3. The same assembled compare result then feeds:
   - `truth_followup`
   - `correction_candidates`
   - `planner_summary`
   - `budget_control`
   - `reference_orchestrator_feedback`
4. `reference_iterate_stage_checkpoint(...)` consumes that one broad compare
   result and advances or blocks the guided flow.

This means packet planning, evidence slicing, extraction, ranking, and synthesis
are all implicitly collapsed into one compare request.

### Target Flow After TASK-166

The public tool names stay the same:

- `reference_compare_stage_checkpoint(...)`
- `reference_iterate_stage_checkpoint(...)`

But internally the path becomes:

1. build one deterministic compare plan from:
   - `guided_flow_state`
   - `assembled_target_scope`
   - selected references
   - active gate blockers
2. split the compare into bounded packets:
   - by view
   - by scope
   - by complexity tier
3. for each packet:
   - run deterministic truth preflight first
   - attach always-on lightweight CV metrics
   - optionally attach advisory-only sidecar evidence
   - ask one narrow LLM question instead of one whole-model prompt
4. merge packet results into one short synthesis result
5. project that synthesis back onto the existing staged compare / iterate
   contracts so downstream clients still read:
   - `reference_understanding_summary`
   - `truth_followup`
   - `correction_candidates`
   - `planner_summary`
   - `budget_control`
   - `reference_orchestrator_feedback`
6. expose richer packet diagnostics only as additive, profile-aware detail on
   the same staged response family, and keep `reference_orchestrator_feedback`
   as the owner of the compact orchestration-facing read model

### Where New Pieces Fit

- View-first and scope-first planning slot into the staged compare path
  **before a final `VisionRequest` is assembled**, and staged packet work must
  start from the earlier capture/truth seams:
  `server/adapters/mcp/vision/capture_runtime.py` for deterministic stage
  captures plus `server/adapters/mcp/areas/reference_truth.py` and
  `server/adapters/mcp/areas/reference_view_diagnostics.py` for truth and
  framing inputs before any final `VisionRequest` assembly.
- Packet planning also owns packet-local capture/reference narrowing so the
  implementation does not degenerate into one packet wrapper around the current
  monolithic `VisionRequest`.
- Deterministic CV and optional PyTorch sidecars slot in **between** truth
  preflight and the narrow packet LLM question.
- Compare-time sidecar execution/projection should stay a staged compare seam
  owned by packet compare helpers/services plus staged response projection; do
  not treat the RU-specific `server/adapters/mcp/vision/reference_support.py`
  module as the default durable owner for packet-evidence execution.
- Two-pass compare splits the current monolithic `run_vision_assist(...)` usage
  into:
  - packet extraction first
  - correction ranking/synthesis second
- Narrow extraction/ranking contract work must update the typed
  `VisionAssistContract` plus the
  `server/adapters/mcp/vision/prompting.py` and
  `server/adapters/mcp/vision/parsing.py` seams;
  `server/adapters/mcp/vision/runner.py` remains the bounded transport and
  budget executor, not the primary prompt/schema owner.
- Configurable budgets replace the current fixed `VISION_ASSIST_POLICY`
  constraint in `server/adapters/mcp/vision/runner.py`, but packet
  decomposition remains the primary scaling mechanism.
- Any new `compare_diagnostics` or typed packet evidence must extend the
  existing staged compare/iterate contracts and feed the existing compact
  `reference_orchestrator_feedback` projection instead of bypassing it.
- Once packet planning, packet execution, or synthesis policy grows beyond light
  staging glue, move it into an explicit `server/application/services/` seam
  and keep `server/adapters/mcp/areas/reference.py` limited to staged compare
  orchestration and public-response projection.

### Multi-Reference Guidance

For 6-12 image sets, the intended generic strategy is:

- compare one view packet or one small paired packet at a time
- persist packet-local evidence and provenance
- produce one short synthesis summary afterward
- keep packet scheduling within the live `runtime.max_images` envelope until
  `TASK-166-05` deliberately changes the runtime budget owner

That makes the family usable for:

- simple models
- complex models
- super-complex models

without requiring one massive all-images compare request.

## Runtime Trigger Matrix

| Event | What Runs | Primary Owner Seams | Outputs Carried Forward | Boundary Role |
|------|------|------|------|------|
| `reference_images(action="attach", ...)` | Existing reference-understanding bootstrap plus optional RU support adapters | `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_images_runtime.py`, `server/adapters/mcp/areas/reference_understanding.py`, `server/adapters/mcp/vision/reference_support.py` | `reference_understanding_summary`, `reference_strategy_state`, optional classifier / segmentation RU evidence | support-only bootstrap context; not staged compare truth authority |
| `reference_compare_stage_checkpoint(...)` | deterministic compare-plan build from guided state, scope, references, and active blockers | `server/adapters/mcp/areas/reference.py` for staged orchestration, `server/application/services/` for durable packet policy, `server/adapters/mcp/areas/reference_planner.py` for staged projection/budget shaping | packet order, packet-local view/scope selection, staged response scaffolding | server-owned deterministic planning |
| per-packet preflight | packet-local truth slice and visibility framing | `scene_scope_graph`, `scene_relation_graph`, `scene_view_diagnostics`, `server/adapters/mcp/areas/reference_truth.py`, `server/adapters/mcp/areas/reference_view_diagnostics.py`, `server/adapters/mcp/vision/capture_runtime.py`, `server/adapters/mcp/vision/capture.py` | packet-local truth inputs, selected captures/references, view ambiguity hints | deterministic truth owner |
| per-packet support evidence | always-on deterministic CV plus optional advisory-only sidecars when policy allows | `server/adapters/mcp/areas/reference_silhouette.py`, `server/adapters/mcp/vision/silhouette.py`, `server/adapters/mcp/areas/reference.py`, `server/application/services/`, and only optional shared adapters/config borrowed from `server/adapters/mcp/vision/reference_support.py` when that RU seam is deliberately generalized | compact CV metrics, optional advisory artifacts, packet-local evidence refs | deterministic support evidence plus advisory-only sidecars; never sole correctness authority |
| per-packet pass 1 | narrow VLM extraction for one packet | `server/adapters/mcp/vision/runner.py`, `server/adapters/mcp/vision/prompting.py`, `server/adapters/mcp/vision/parsing.py` | bounded extraction findings, packet status | bounded visual support on top of truth inputs |
| per-packet pass 2 | ranking and synthesis only when extraction warrants it | `server/adapters/mcp/areas/reference.py` for staged orchestration, `server/application/services/` for ranking/synthesis policy, `server/adapters/mcp/areas/reference_planner.py` for staged projection, `server/adapters/mcp/vision/runner.py` for bounded assistant execution | ranked packet guidance, packet conflict notes, synthesis inputs | derived compare guidance, not a second truth source |
| staged compare projection | project packet synthesis onto the existing staged compare contract | `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/areas/reference_feedback.py` | `truth_followup`, `correction_candidates`, `planner_summary`, `budget_control`, `reference_orchestrator_feedback`, additive `compare_diagnostics` when needed | existing public response family; no second flow |
| `reference_iterate_stage_checkpoint(...)` | consume staged compare output and advance or hold the loop | `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_feedback.py` | `correction_focus`, `loop_disposition`, updated `reference_orchestrator_feedback`, optional compacted nested compare payload | existing iterative loop owner consuming packet synthesis rather than raw packet internals |

### Classifier Role Clarification

- Attach-time classifier support stays on the existing `TASK-163`
  `reference_understanding` path as global bootstrap context.
- Compare-time classifier usage is packet-local and advisory when enabled.
- Mid-flow authority remains with deterministic truth plus bounded CV/support
  evidence; classifier support must not become the main packet-comparison
  engine.

## Execution Structure

| Order | Task | Purpose |
|------|------|---------|
| 1 | [TASK-166-01](./TASK-166-01_View_And_Scope_Packet_Compare_Family.md) | Define the packet family that decomposes compare by view and active scope |
| 2 | [TASK-166-02](./TASK-166-02_Truth_First_Two_Pass_Compare_Execution.md) | Split compare into deterministic preflight, narrow extraction, and later correction ranking |
| 3 | [TASK-166-03](./TASK-166-03_Deterministic_CV_And_Optional_PyTorch_Perceiver_Sidecars.md) | Add always-on lightweight CV and optional heavy perception adapters as support evidence |
| 4 | [TASK-166-04](./TASK-166-04_Complexity_Tiers_And_Multi_Reference_Scaling_Policy.md) | Make the family scale from simple to super-complex 6-12 image runs |
| 5 | [TASK-166-05](./TASK-166-05_Configurable_Vision_Assist_Budgets_And_Runtime_Overrides.md) | Expose configurable compare budgets and runtime diagnostics instead of one hard-coded assistant gate |
| 6 | [TASK-166-06](./TASK-166-06_Public_Contract_Transparency_For_Hierarchical_Compare.md) | Add additive packet transparency and compact feedback projection on the existing staged compare/iterate contracts |

## Repository Touchpoints

| Path / Module | Expected Ownership | Why It Is In Scope |
|---------------|--------------------|--------------------|
| `server/adapters/mcp/areas/reference.py` | Stage compare/iterate assembler | Current monolithic payload owner; should remain orchestration-first rather than the long-term home for packet policy |
| `server/adapters/mcp/areas/reference_planner.py` | Packet synthesis and staged budget policy | Already owns trimming and planner shaping, so budget/runtime work must keep this seam aligned with the runner and staged contract |
| `server/adapters/mcp/areas/reference_feedback.py` | Compact orchestrator read model | Must keep owning compact projection instead of forcing orchestrators to parse raw packet detail |
| `server/adapters/mcp/contracts/reference.py` | Public compare/iterate contracts | Any packet/synthesis/budget metadata must be declared explicitly |
| `server/adapters/mcp/vision/capture_runtime.py` | Staged compare capture preset and scene-state seam | Packet-local view planning must stay aligned with the live stage-capture owner before any final request assembly happens |
| `server/adapters/mcp/vision/capture.py` | Final capture/reference request assembly seam | Packet-local capture/reference narrowing may still affect request assembly, but this is the later assembly layer, not the sole owner of staged compare planning |
| `server/adapters/mcp/sampling/result_types.py` | Typed vision result contract | Extraction/ranking split and additive diagnostics must stay schema-first instead of becoming ad-hoc dict packing |
| `server/adapters/mcp/vision/prompting.py`, `server/adapters/mcp/vision/parsing.py` | Narrow compare prompt/schema/parser contract | Packet extraction and ranking split changes live here, not only in the runner transport layer |
| `server/adapters/mcp/vision/runner.py` | Bounded `vision_assist` transport and budget enforcement | Current fixed `max_input_chars=12000` lives here, but the runner should not become the only owner of compare-time prompt/schema changes |
| `server/adapters/mcp/vision/runtime.py`, `server/adapters/mcp/vision/config.py`, `server/adapters/mcp/vision/backends.py` | Runtime/provider config | Own provider/model budgets and request assembly |
| `server/adapters/mcp/vision/reference_support.py` | RU support and optional shared sidecar adapter/config seam | Existing RU support owner that compare-time sidecars may borrow from deliberately, but it is not the default durable owner for staged packet-evidence execution or operator-facing compare-time config |
| `server/application/services/` | Framework-free compare policy | Non-trivial packet planning, packet execution ordering, and synthesis policy should live outside the FastMCP tool wrapper so `server/adapters/mcp/areas/reference.py` stays orchestration-only |
| `tests/unit/adapters/mcp/test_reference_images.py` | Compare/iterate owner lane | Most compare payload/budget logic already lives here |
| `tests/e2e/vision/`, `tests/e2e/integration/` | Runtime proof lanes | Need multi-view and multi-reference runtime proof |
| `README.md`, `_docs/AVAILABLE_TOOLS_SUMMARY.md`, `_docs/_VISION/README.md`, `_docs/_MCP_SERVER/README.md`, `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`, `_docs/_TESTS/README.md`, `_docs/_TASKS/README.md` | Canonical docs and board state | Must reflect the new compare architecture, public tool surface, validation map, operator knobs, and operator-facing client/runtime config examples |

## Test Matrix

| Slice | Primary Validation Lane | Why |
|------|--------------------------|-----|
| packet planning by view/scope | unit reference-image / planner tests | deterministic policy |
| truth-first two-pass compare | unit compare/runner tests plus targeted E2E | contract split must be explicit |
| lightweight CV and optional sidecars | unit CV/reference support lanes plus selected runtime proof | keeps deterministic and optional evidence roles clear |
| 6-12 image scaling | unit packet synthesis + optional live compare proof | main scaling goal |
| configurable budgets | unit runtime/runner/script tests | operator tuning must be explicit and testable |
| additive compare transparency | unit staged compare/iterate/reference-feedback tests | packet detail must stay additive while the compact orchestrator read model remains first-class |

## Acceptance Criteria

- compare/iterate can process one view packet or one scope packet without
  carrying every view and every part in one request
- simple, complex, and super-complex runs use different packet/synthesis
  strategies while preserving one generic family
- deterministic CV and optional PyTorch sidecars feed compact packet evidence to
  the LLM instead of leaving all low-level perception to one large prompt
- compare assistant budgets are configurable and visible in diagnostics
- packet provenance, pass status, conflicts, and budget pressure can surface
  additively on the existing staged compare / iterate contracts without
  renaming or removing the current fields
- `reference_orchestrator_feedback` remains the compact owner seam for LLM
  orchestration and can project packet uncertainty/provenance without requiring
  raw packet parsing
- compact feedback projection stays explicit and typed at the builder boundary:
  - packet rationale / dominant evidence -> `evidence_summary`
  - packet conflicts, skipped ranking, and budget clipping -> `uncertainty_notes`
  - merged actionable packet outputs -> `correction_focus`
  - any packet/budget condition that changes the next safe step must surface
    through the existing message/next-action path rather than ad-hoc raw packet
    parsing
- the final family remains generic across creature, architecture, organ, and
  character domains

## Progress Notes

- 2026-05-08: first packeted staged-compare slice landed on the existing
  `reference_compare_stage_checkpoint(...)` /
  `reference_iterate_stage_checkpoint(...)` family:
  - staged compare now builds deterministic compare packets from the staged
    view set, active scope, and truth-followup focus pairs instead of assuming
    one always-monolithic request shape
  - packet-local staged compare execution now narrows captures, reference ids,
    and truth-summary payloads per packet before calling `vision_assist`
  - compact packet synthesis now merges successful packet results back into the
    existing staged compare contract, and additive `compare_diagnostics` can
    surface packet ids, pass state, packet-local scope/view selection, and
    budget/conflict notes on rich or uncertainty paths
  - `reference_orchestrator_feedback` now accepts packet diagnostics as a
    first-class summary input instead of forcing orchestrators to inspect raw
    packet payloads
- 2026-05-08: packet-specific vision contract follow-up landed for the staged
  compare path:
  - packet-local compare requests now use an explicit packet mode in the
    prompt/schema/parser seams
  - packet-local `vision_assist` output can now carry typed
    `packet_guidance.packet_status`, `status_reason`, and
    `ranking_recommendation`
  - staged compare now maps packet status from the parsed packet contract into
    `compare_diagnostics` instead of inferring everything from generic mismatch
    lists
- 2026-05-08: `TASK-166-02-02` is now closed:
  - packet extraction and packet ranking are now two bounded staged compare
    phases instead of one always-large packet call
  - ranking is skipped explicitly for clean / low-information / blocked
    extraction outcomes
  - ranking failure now preserves extraction evidence and projects explicit
    `ranking_status="error"` uncertainty through `compare_diagnostics`
- 2026-05-08: `TASK-166-03-01` is now closed:
  - compare-time silhouette/action-hint evidence now feeds packet-local
    `support_evidence` before packet extraction/ranking runs
  - packet compare requests now receive compact deterministic CV summaries in
    metadata/payload instead of discovering those facts only after the compare
    response is assembled
- 2026-05-08: follow-up repair pass tightened the shipped packet/runtime
  contract:
  - packet planning now runs through
    `server/application/services/reference_compare_packets.py`, so durable
    view/scope policy and synthesis/merge rules are no longer concentrated only
    inside the MCP adapter layer
  - simple runs now emit explicit per-view packets, and complex runs now keep
    both packet-local view and scope slices together instead of dropping
    secondary views once focus pairs exist
  - semantic scope clusters now surface common creature buckets such as
    `Body + Head`, `Tail`, and `Ears` on packet diagnostics
  - packet-local `support_evidence` is now typed and packet-scoped, with
    capture/reference provenance preserved on each packet item
  - clean compact single-packet runs can omit additive `compare_diagnostics`
    again, while compact ranking failures still force explicit packet
    diagnostics through the public staged response
  - packet synthesis now dedupes reused capture/reference counts instead of
    overstating the final staged compare input summary
- 2026-05-08: remaining follow-on work still includes the deeper TASK-166
  leaves for packet-specific prompt/parser contract hardening, explicit
  extraction-vs-ranking phase semantics, deterministic CV / optional PyTorch
  sidecars, richer complexity-tier scaling for 6-12 image sets, and runtime
  budget overrides.

## Docs To Update

- `README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `_docs/_TESTS/README.md`
- `_docs/_TASKS/README.md`

## Changelog Impact

- one umbrella `_docs/_CHANGELOG/` entry when the packeted compare family ships

## Status / Board Update

- keep the promoted `TASK-166` row aligned with all open/closed `TASK-166-*`
  subtasks and leaves in `_docs/_TASKS/README.md`
- when the umbrella closes, record which follow-on items remain explicit
  standalone tasks rather than leaving open descendants under a closed parent

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/router/application/test_router_contracts.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`
