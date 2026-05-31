# TASK-183: Capability-Enriched Vision Schema And Deterministic Cross-Check

**Status:** ✅ Done
**Completed:** 2026-05-30
**Completion Summary:** TASK-183-01 (capability-aware findings schema + curated payload + backend findings/truncation passthrough fix, changelog 374) and TASK-183-02 (silhouette threshold calibration + IoU convergence signal, changelog 380) shipped, with audit drift closed by changelog 389: schema/key selection now receives `model_capabilities`, the default external payload is curated instead of raw `metadata`, provider token usage/finish reason surfaces in capability summaries, and a lightweight deterministic silhouette consistency score is attached to support evidence and iterate-loop convergence. The optional heavy render-vs-reference embedding cross-check (MEt3R/DINO) stays a default-off sidecar follow-on per the runtime boundary.
**Priority:** 🟡 Medium
**Category:** Vision / Capability-Aware Schema And Calibration
**Estimated Effort:** Large
**Follow-on After:** [TASK-140](./TASK-140_Expand_External_Vision_Contract_Profiles_Across_Qwen_Anthropic_OpenAI_And_NVIDIA.md), [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md)
**Related:** [TASK-178](./TASK-178_Structured_Per_Finding_Compare_Schema.md), [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md), [TASK-169](./TASK-169_Reference_Guided_Quality_Drift_Regression_And_Runtime_Authority.md)

## Relationship To Existing Board Items

- This umbrella is a standalone follow-on family, not a child of the parents it
  references. `TASK-140` and `TASK-172` are linked through **Follow-on After:**
  because they own upstream seams this work extends, not because this family
  lives under them. Its own subtasks use **Parent:** pointing back here.
- `TASK-140-06` (🚧 In Progress) is landing the model-capability substrate
  (`VisionModelCapabilities` at `vision/config.py:33` and the reviewed fallback
  registry at `vision/model_profiles/openrouter_openai.py`). This family is a
  **consumer** of that substrate: it threads `model_capabilities` into the
  response-schema builder and payload framing, which the substrate does not yet
  do. It must not reopen the `TASK-140-06` provider-capability
  substrate or add new provider catalog plumbing.
- `TASK-172` shipped the optional-runtime seam (default-off
  classifier/localization/segmentation sidecars, e.g.
  `VisionSegmentationSidecarConfig` at `vision/config.py:390` and
  `VisionLocalizationConfig` at `vision/config.py:405`). The heavier
  render-vs-reference embedding variant added here reuses that exact default-off,
  advisory-only, packet-bounded seam; it does not add a new always-on heavy
  dependency.
- `TASK-178` proposes typed per-finding compare fields. This family is the gate
  that decides **when** the richer per-finding/per-mark schema is emitted at all:
  strong, grounding-capable models with ample completion-token budget get it;
  weak/local models keep the lean schema. The two families are complementary —
  `TASK-178` owns the finding shape, `TASK-183` owns the capability-gated
  emission and the deterministic cross-check that down-weights it.
- `TASK-166` owns the hierarchical packet compare and deterministic CV evidence
  taxonomy (`reference_silhouette.py`); the silhouette-threshold calibration and
  render-vs-reference consistency score here flow through that same evidence
  channel. `TASK-169` owns the runtime-authority and quality-drift regression
  posture this family must not weaken.

## Objective

Make the LLM-facing vision output match the receiving model's real capability,
and add a deterministic geometry cross-check that keeps advisory vision honest:

- thread `model_capabilities` (already resolved by `TASK-140-06`) into
  `build_vision_response_json_schema` (`vision/prompting.py:851`) so a frontier
  grounding/structured-output model receives the richer per-finding and per-mark
  schema while a tiny local model keeps the lean prose schema it can actually
  satisfy
- stop defaulting nearly every strong hosted model to the field-dropping
  `google_family_compare` profile (`vision/runtime.py:54`), or backfill its
  dropped fields, so frontier models can return
  `visible_changes`/`likely_issues`/`recommended_checks`/`confidence`/`captures_used`
- replace the bare `json.dumps` default external payload
  (`vision/prompting.py:747-755`) with curated, task-framed scaffolding that
  strips internal IDs before they reach the provider
- capture and surface provider token usage (completion tokens vs cap) so
  truncated structured responses are observable instead of silently malformed
- add a deterministic render-vs-reference consistency score each cycle to flag
  VLM-vs-geometry disagreement, down-weight unverified visual claims, and act as
  a monotonic convergence/stop signal across iterations
- calibrate the silhouette severity thresholds (`vision/silhouette.py`) against a
  golden fixture with a regression test, normalize `aspect_ratio_delta` onto the
  band/IoU scale, and either wire up or drop the dead `mid_band`/`lower_band`
  metrics

## Business Problem

The current vision-to-LLM path under-serves strong models and over-trusts weak
visual claims, both grounded in verified repo behavior:

- `build_vision_response_json_schema` (`vision/prompting.py:851`) accepts
  `vision_contract_profile`, `provider_name`, and `request`, but **never**
  `model_capabilities`. A frontier grounding-capable model and a tiny local
  model therefore receive the same schema; the builder cannot offer the richer
  per-finding fields even when the model could clearly satisfy them.
- `_resolve_vision_contract_profile` (`vision/runtime.py:54`) routes almost every
  strong hosted model to `google_family_compare`: any Google-family model, any
  OpenAI-family model on OpenRouter (`vision/runtime.py:69`), and anything on
  `google_ai_studio` (`vision/runtime.py:71`). The reviewed fallback profiles
  reinforce this — e.g. `anthropic/claude-opus-4.6`, `openai/gpt-5.4`, and the
  Gemini families all carry `preferred_contract_profile="google_family_compare"`
  in `vision/model_profiles/openrouter_openai.py`. That profile's schema
  (`vision/prompting.py:1245`) **drops** `visible_changes`, `likely_issues`,
  `recommended_checks`, `confidence`, and `captures_used` that the
  `generic_full` schema (`vision/prompting.py:1259`) carries, so the strongest
  models return the least structured evidence.
- The default external payload (`vision/prompting.py:747-755`) is a bare
  `json.dumps` of `goal`, `target_object`, `prompt_hint`, `truth_summary`,
  `metadata`, and per-image `role`/`label`. It has no task framing and leaks raw
  internal `metadata`/labels straight to the provider.
- Provider token usage is discarded: `_extract_message_text`
  (`vision/backends.py:87`) reads only `choices[0].message.content` and ignores
  the `usage` block; the Gemini path likewise ignores `usageMetadata`. When a
  structured response is truncated at the completion-token cap it surfaces as a
  generic parse failure with no "you hit the cap" signal, even though the cap is
  known (`model_max_completion_tokens` is already summarized at
  `vision/backends.py:304`).
- The deterministic silhouette analysis (`vision/silhouette.py`) uses
  uncalibrated magic-number thresholds. `mask_iou` is scored against a fixed
  `reference_value=1.0` ideal with `high=0.35`/`medium=0.18`
  (`vision/silhouette.py:253-256`), `aspect_ratio_delta` reuses the same
  `0.35`/`0.18` band even though it is an unnormalized ratio difference, not a
  band fraction (`vision/silhouette.py:266-271`), and the band metrics
  `mid_band_width_delta`/`lower_band_width_delta` are computed
  (`vision/silhouette.py:276-277`) but never consumed by
  `build_action_hints_from_silhouette` in
  `areas/reference_silhouette.py`. An IoU=1.0 ideal is unattainable across
  mismatched reference/capture views, there is no monotonic "closer than last
  cycle" signal, and the `confidence` field is non-range-validated and explicitly
  distrusted downstream.

The net effect: the orchestrating LLM gets thin, ID-leaking, capability-blind
evidence from the best models, and an uncalibrated geometry signal that cannot
tell improvement from drift.

## Business Outcome

After this umbrella lands:

- a frontier grounding/structured-output model with ample completion budget
  receives the richer per-finding/per-mark schema, while a small local model
  keeps the lean schema it can satisfy without truncating
- strong hosted models stop silently losing
  `visible_changes`/`likely_issues`/`recommended_checks`/`confidence`/`captures_used`
  to the `google_family_compare` default
- the external payload is curated, task-framed, and free of leaked internal IDs
- truncated structured responses are observable as a token-cap event, not an
  anonymous parse failure
- a deterministic render-vs-reference consistency score flags when the VLM and
  the geometry disagree, down-weights unverified visual claims, and gives the
  orchestrator a monotonic convergence/stop signal across cycles
- silhouette severity thresholds are calibrated against a golden fixture and
  defended by a regression test, with `aspect_ratio_delta` on a comparable scale
  and no dead band metrics

## Non-Goals

- vision stays **advisory**. New structured fields and the consistency score are
  still VLM/heuristic interpretation and must keep
  `not_truth_source` / `requires_deterministic_checks_for_correctness`.
  Deterministic inspection/assertion/silhouette own scene truth; vision must not
  mark gates complete or unlock tools.
- magnitudes stay **proportional ratios** versus a trusted reference anchor,
  never authoritative absolute measurements (VLMs land within 2x on roughly 37%
  of metric tasks); the richer schema must not invite absolute metric claims.
- heavier perception/embedding models (CLIP/DINO embeddings, MEt3R/DUSt3R-style
  render-vs-reference networks, SAM/SAM2/GroundingDINO/Depth-Anything) stay
  **default-off**, advisory-only, and packet-bounded behind the existing
  `TASK-172` optional-runtime seam. Do not add a new always-on heavy dependency
  and do not reopen the `TASK-140-06` provider-capability substrate.
- do not emit raw coordinate tokens as primary evidence (they degrade LLM
  spatial reasoning: 3DGraphLLM 50.1->42.6; text-scene relations 59.4 vs coords
  18.4). Prefer symbolic relations + ratios; coordinates on demand only.
- do not add VLM-side chain-of-thought for spatial judgments (VSI-Bench
  regression of roughly -1..-21%); reasoning stays in the orchestrator.
- do not make the lean schema worse for small models in pursuit of the rich one,
  and do not weaken the existing fail-safe completion-token clip or over-budget
  rejection.

## Execution Structure

| Order | Task | Purpose |
|------|------|---------|
| 1 | [TASK-183-01](./TASK-183-01_Capability_Aware_Response_Schema_And_Curated_Payload.md) | Capability-Aware Response Schema And Curated Payload |
| 2 | [TASK-183-02](./TASK-183-02_Deterministic_Cross_Check_And_Silhouette_Threshold_Calibration.md) | Deterministic Cross-Check And Silhouette Threshold Calibration |

## Repository Touchpoints

| Path / Module | Expected Ownership | Why It Is In Scope |
|---------------|--------------------|--------------------|
| `server/adapters/mcp/vision/prompting.py` | response-schema builder and external payload framing | `build_vision_response_json_schema` (`:851`) never receives `model_capabilities`; the `google_family_compare` schema drops fields (`:1245`); the default payload is a bare `json.dumps` (`:747-755`) that leaks internal IDs |
| `server/adapters/mcp/vision/runtime.py` | contract-profile routing | `_resolve_vision_contract_profile` (`:54`) defaults strong hosted models to the field-dropping `google_family_compare`; this family decides when frontier models should keep `generic_full` (or the richer schema) |
| `server/adapters/mcp/vision/backends.py` | request assembly and provider-usage capture | all three `build_vision_response_json_schema` call sites (`:807`, `:826`, `:888`) must learn capabilities; `_extract_message_text` (`:87`) ignores `usage`/`usageMetadata`, so truncation against the known cap (`:304`) is invisible |
| `server/adapters/mcp/vision/model_profiles/openrouter_openai.py` | reviewed fallback capability profiles | the `preferred_contract_profile` and `max_completion_tokens` fields on these profiles drive the capability gate; this family reads them, it does not add new catalog plumbing |
| `server/adapters/mcp/vision/silhouette.py` | deterministic silhouette metrics | uncalibrated thresholds (`mask_iou` `high=0.35` at `:256`), an unattainable `reference_value=1.0` IoU ideal (`:253`), `aspect_ratio_delta` on the wrong scale (`:266-271`), and dead `mid_band`/`lower_band` metrics (`:276-277`) all live here |
| `server/adapters/mcp/areas/reference_silhouette.py` | silhouette evidence/action-hint projection | the dead band metrics are never consumed here; `build_action_hints_from_silhouette` and `build_compare_support_evidence` must consume calibrated metrics and the new consistency score as advisory evidence |
| `server/adapters/mcp/contracts/reference.py` | silhouette / compare-support evidence contracts | `ReferenceSilhouetteMetricContract` / `ReferenceSilhouetteAnalysisContract` / `ReferenceCompareSupportEvidenceContract` are the typed surfaces the calibrated metrics and the new consistency score project through (matches `TASK-183-02`'s touchpoint list) |
| `server/adapters/mcp/vision/evaluation.py` | golden harness scoring | the calibration and consistency-score regression must score against `VisionGoldenScenario`/`evaluate_vision_result` golden fixtures, not against hand-picked constants |
| `server/adapters/mcp/vision/config.py` | typed runtime/optional-sidecar config | the optional heavy render-vs-reference variant must reuse the default-off sidecar config shape (`VisionSegmentationSidecarConfig`/`VisionLocalizationConfig`) and `VisionModelCapabilities` |
| `tests/unit/adapters/mcp/`, `tests/e2e/vision/`, `tests/fixtures/vision_eval/` | proof lanes and golden fixtures | capability-gated schema, curated payload, usage surfacing, threshold calibration, and consistency-score behavior must be proven on repo-owned fixtures |

## Test Matrix

| Slice | Primary Validation Lane | Why |
|------|--------------------------|-----|
| capability-gated response schema | `tests/unit/adapters/mcp/test_vision_runtime_config.py`, `tests/unit/adapters/mcp/test_vision_prompting.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py` | strong vs weak capabilities must select rich vs lean schema, and frontier models must stop defaulting to the field-dropping compare profile |
| curated, ID-stripped payload | `tests/unit/adapters/mcp/test_vision_prompting.py`, `tests/unit/adapters/mcp/test_vision_external_backend.py` | the default payload must be task-framed and must not leak internal `metadata`/IDs |
| provider token-usage surfacing | `tests/unit/adapters/mcp/test_vision_external_backend.py` | truncation against the known completion cap must be observable instead of an anonymous parse failure |
| silhouette threshold calibration | `tests/unit/adapters/mcp/test_vision_silhouette.py`, `tests/fixtures/vision_eval/` | thresholds must be defended by a golden regression, with `aspect_ratio_delta` rescaled and dead band metrics resolved |
| deterministic render-vs-reference consistency score | `tests/unit/adapters/mcp/test_vision_silhouette.py`, `tests/unit/adapters/mcp/test_vision_evaluation.py`, `tests/e2e/vision/test_reference_stage_silhouette_contract.py` | the score must flag VLM-vs-geometry disagreement, stay advisory/default-off for the heavy variant, and behave monotonically across cycles |

## Acceptance Criteria

- given strong `model_capabilities` (advertised `structured_outputs`/`response_format`
  plus ample `max_completion_tokens`), `build_vision_response_json_schema`
  returns the richer per-finding/per-mark schema; given weak capabilities it
  returns the lean schema, observably and deterministically
- frontier hosted models no longer default to `google_family_compare` (or that
  profile no longer drops
  `visible_changes`/`likely_issues`/`recommended_checks`/`confidence`/`captures_used`)
- the default external payload is curated/task-framed and contains no leaked
  internal `metadata` or internal IDs
- when a structured response is truncated at the completion-token cap, the run
  surfaces a token-cap/truncation diagnostic rather than an anonymous parse
  failure
- silhouette severity thresholds are calibrated against a golden fixture and
  defended by a regression test; `aspect_ratio_delta` is on a band/IoU-comparable
  scale; `mid_band_width_delta`/`lower_band_width_delta` are either consumed by
  an action hint / evidence projection or removed
- a deterministic render-vs-reference consistency score is produced each cycle,
  flags VLM-vs-geometry disagreement, down-weights unverified visual claims, and
  exposes a monotonic convergence/stop signal; the heavy embedding variant stays
  default-off behind the `TASK-172` seam
- all new fields keep `not_truth_source` /
  `requires_deterministic_checks_for_correctness`; vision still cannot pass gates
  or unlock tools
- research caveat: the cited benchmarks (3DGen-Bench, VLM3D, GPTEval3D, MEt3R,
  Point-Bind, IR3D-Bench) are indoor-scan/synthetic and **not**
  Blender-vs-reference. Re-measure absolute gains on `tests/fixtures/vision_eval`
  golden fixtures before promoting either slice past planning

## Docs To Update

- `_docs/_TASKS/README.md`
- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_VISION/HYBRID_LOOP_REAL_CREATURE_EVAL.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- split across the execution slices below; each child task owns its exact lane

## Changelog Impact

- planning-only now; add a `_docs/_CHANGELOG/*` entry when the first slice lands
- do not treat this planning-only task creation as the changelog event

## Status / Board Update

- `_docs/_TASKS/README.md` should track `TASK-183` as a promoted open item on the
  Vision / Hybrid Loop lane
- child tasks stay nested under the open umbrella and do not need board rows
  unless one later becomes a separately promoted follow-on

## Validation Commands

- `git diff --check`
- `rg -n "TASK-183|Capability-Enriched Vision Schema And Deterministic Cross-Check|Capability-Aware Response Schema And Curated Payload|Deterministic Cross-Check And Silhouette Threshold Calibration|not_truth_source|google_family_compare" _docs/_TASKS/TASK-183*.md`

## Validation Category

- planning / governance / task-family definition
