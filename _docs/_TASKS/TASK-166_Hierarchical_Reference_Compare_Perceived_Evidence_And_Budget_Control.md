# TASK-166: Hierarchical Reference Compare, Perceived Evidence, And Budget Control

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Vision / Hybrid Loop / Guided Runtime
**Estimated Effort:** Large
**Follow-on After:** [TASK-145](./TASK-145_Spatial_Repair_Planner_And_Sculpt_Handoff_Context.md), [TASK-163](./TASK-163_Vision_Orchestrator_Feedback_Strategy_Normalization_And_Optional_Perception_Adapters.md), [TASK-140-06](./TASK-140-06_OpenRouter_Model_Capability_Aware_Vision_Runtime.md)
**Related:** [TASK-122-03-06](./TASK-122-03-06_Hybrid_Loop_Model_Aware_Budget_And_Scope_Control.md), [TASK-135](./TASK-135_Anatomy_Aware_Reference_Guided_Low_Poly_Creature_Reconstruction.md), [TASK-136](./TASK-136_Reference_Guided_Architecture_And_Building_Reconstruction.md), [TASK-137](./TASK-137_Anatomy_Aware_Reference_Guided_Organ_Reconstruction.md), [TASK-138](./TASK-138_Anatomy_Aware_Reference_Guided_Biped_And_Fantasy_Character_Reconstruction.md), [TASK-160](./TASK-160_Guided_Client_Feedback_And_Streamable_HTTP_Recovery_UX.md)
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
   - optionally attach support-only sidecar evidence
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

- View-first and scope-first planning slot in **before**
  `build_vision_request_from_stage_captures(...)`.
- Packet planning also owns packet-local capture/reference narrowing so the
  implementation does not degenerate into one packet wrapper around the current
  monolithic `VisionRequest`.
- Deterministic CV and optional PyTorch sidecars slot in **between** truth
  preflight and the narrow packet LLM question.
- Two-pass compare splits the current monolithic `run_vision_assist(...)` usage
  into:
  - packet extraction first
  - correction ranking/synthesis second
- Configurable budgets replace the current fixed `VISION_ASSIST_POLICY`
  constraint in `vision/runner.py`, but packet decomposition remains the primary
  scaling mechanism.
- Any new `compare_diagnostics` or typed packet evidence must extend the
  existing staged compare/iterate contracts and feed the existing compact
  `reference_orchestrator_feedback` projection instead of bypassing it.

### Multi-Reference Guidance

For 6-12 image sets, the intended generic strategy is:

- compare one view packet or one small paired packet at a time
- persist packet-local evidence and provenance
- produce one short synthesis summary afterward

That makes the family usable for:

- simple models
- complex models
- super-complex models

without requiring one massive all-images compare request.

## Runtime Trigger Matrix

| Event | What Runs | Primary Owner Seams | Outputs Carried Forward | Boundary Role |
|------|------|------|------|------|
| `reference_images(action="attach", ...)` | Existing reference-understanding bootstrap plus optional RU support adapters | `areas/reference_understanding.py`, `vision/reference_support.py` | `reference_understanding_summary`, `reference_strategy_state`, optional classifier / segmentation RU evidence | support-only bootstrap context; not staged compare truth authority |
| `reference_compare_stage_checkpoint(...)` | deterministic compare-plan build from guided state, scope, references, and active blockers | `areas/reference.py`, `areas/reference_planner.py` | packet order, packet-local view/scope selection, staged response scaffolding | server-owned deterministic planning |
| per-packet preflight | packet-local truth slice and visibility framing | `scene_scope_graph`, `scene_relation_graph`, `scene_view_diagnostics`, `vision/capture.py` | packet-local truth inputs, selected captures/references, view ambiguity hints | deterministic truth owner |
| per-packet support evidence | always-on CV plus optional sidecars when policy allows | `vision/reference_support.py`, `areas/reference_silhouette.py` | compact metrics, optional advisory artifacts, packet-local evidence refs | support-only / advisory support; never sole correctness authority |
| per-packet pass 1 | narrow VLM extraction for one packet | `vision/runner.py`, compare prompting/parsing seams | bounded extraction findings, packet status | bounded visual support on top of truth inputs |
| per-packet pass 2 | ranking and synthesis only when extraction warrants it | `areas/reference.py`, `areas/reference_planner.py`, `vision/runner.py` | ranked packet guidance, packet conflict notes, synthesis inputs | derived compare guidance, not a second truth source |
| staged compare projection | project packet synthesis onto the existing staged compare contract | `areas/reference.py`, `contracts/reference.py`, `areas/reference_feedback.py` | `truth_followup`, `correction_candidates`, `planner_summary`, `budget_control`, `reference_orchestrator_feedback`, additive `compare_diagnostics` when needed | existing public response family; no second flow |
| `reference_iterate_stage_checkpoint(...)` | consume staged compare output and advance or hold the loop | `areas/reference.py`, `areas/reference_feedback.py` | `correction_focus`, `loop_disposition`, updated `reference_orchestrator_feedback`, optional compacted nested compare payload | existing iterative loop owner consuming packet synthesis rather than raw packet internals |

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
| `server/adapters/mcp/areas/reference.py` | Stage compare/iterate assembler | Current monolithic payload owner |
| `server/adapters/mcp/areas/reference_planner.py` | Packet synthesis and budget policy | Already owns trimming and planner shaping |
| `server/adapters/mcp/areas/reference_feedback.py` | Compact orchestrator read model | Must keep owning compact projection instead of forcing orchestrators to parse raw packet detail |
| `server/adapters/mcp/contracts/reference.py` | Public compare/iterate contracts | Any packet/synthesis/budget metadata must be declared explicitly |
| `server/adapters/mcp/vision/capture.py` | Capture/reference request assembly | Packet-local capture/reference narrowing must happen here or at its caller, not only at the outer compare wrapper |
| `server/adapters/mcp/vision/runner.py` | `vision_assist` budget policy | Current fixed `max_input_chars=12000` lives here |
| `server/adapters/mcp/vision/runtime.py`, `vision/config.py`, `vision/backends.py` | Runtime/provider config | Own provider/model budgets and request assembly |
| `server/adapters/mcp/vision/reference_support.py` | Optional classifier / segmentation support | Existing sidecar support owner that this family should extend, not duplicate |
| `server/application/services/` (new helper if needed) | Framework-free compare policy | Packet planning and synthesis should move out of the MCP area once non-trivial |
| `tests/unit/adapters/mcp/test_reference_images.py` | Compare/iterate owner lane | Most compare payload/budget logic already lives here |
| `tests/e2e/vision/`, `tests/e2e/integration/` | Runtime proof lanes | Need multi-view and multi-reference runtime proof |
| `_docs/_VISION/README.md`, `_docs/_MCP_SERVER/README.md`, `_docs/_TASKS/README.md` | Canonical docs and board state | Must reflect the new compare architecture and operator knobs |

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
