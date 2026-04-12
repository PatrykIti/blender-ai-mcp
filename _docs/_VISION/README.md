# Vision Layer Docs

Working documentation for the `TASK-121` vision-assist layer.

This folder is the canonical place to describe:

- pluggable vision backend strategy (`transformers_local` / `openai_compatible_external`)
- request-bound runtime behavior
- deterministic capture-bundle inputs
- goal-scoped reference image context
- macro/workflow integration of `capture_bundle` and `vision_assistant`
- evaluation constraints and model-comparison notes
- real hybrid-loop creature regression guidance

## Related Spatial Docs

Use these companion docs when the work crosses from bounded vision/runtime
details into broader LLM spatial reasoning or product-surface strategy:

- [LLM Guide v2](../LLM_GUIDE_V2.md)
- [Spatial Intelligence Research Brief](../FEATURES_LLM_GUIDE_V1.md)
- [Spatial Intelligence Upgrade Proposal](../Spacial-intelligence-upgrades-for-blender-ai-mcp.md)

## Current State

The repo now has the first implementation scaffolding for the vision layer:

- lazy, optional vision runtime config and backend resolution
- local and external backend families
- explicit external `vision_contract_profile` resolution separate from
  provider transport identity
- bounded `VisionAssistContract` / `VisionAssistantContract`
- richer optional result semantics for later correction loops:
  - `shape_mismatches`
  - `proportion_mismatches`
  - `correction_focus`
  - `next_corrections`
- explicit boundary metadata in the result contract via `boundary_policy`
- deterministic capture-bundle contracts and initial runtime presets:
  - default `compact` profile:
    - `context_wide`
    - `target_front`
    - `target_side`
    - `target_top`
  - available `rich` profile scaffold:
    - `context_wide`
    - `target_focus`
    - `target_oblique_left`
    - `target_oblique_right`
    - `target_front`
    - `target_side`
    - `target_top`
    - `target_detail`
- focus-oriented presets now isolate the target object when the scene helper
  can do so, then restore prior visibility after capture
- goal-scoped `reference_images` session surface
- explicit `guided_reference_readiness` payload on `router_set_goal(...)`,
  `router_get_status()`, `reference_compare_stage_checkpoint(...)`, and
  `reference_iterate_stage_checkpoint(...)`
- bounded `reference_compare_checkpoint(...)` surface for comparing one current
  stage/checkpoint image against the active goal plus attached references
- bounded `reference_compare_current_view(...)` surface for capture-then-compare
  on the current viewport/camera path during staged manual work
- bounded `reference_compare_stage_checkpoint(...)` surface for deterministic
  multi-view stage capture + compare during staged manual/reference-guided work
- bounded `reference_iterate_stage_checkpoint(...)` surface for session-aware
  staged correction loops with repeated-focus detection and continuation hints
- pending references can now stay staged until the goal session is actually
  ready, then adopt automatically on the active guided goal
- blocked same-goal sessions now keep newly staged refs separate from the
  already-active goal refs, while `reference_images(...)` still shows one
  combined visible set for operator-facing list/remove/clear behavior
- ready sessions that still carry explicit pending refs for another goal now
  keep that same visible-set contract consistent: if those refs are visible,
  `reference_images(action="remove"| "clear", ...)` also updates pending state
  instead of leaving broken pending file paths behind
- staged compare/iterate now fail fast with machine-readable readiness data:
  - `blocking_reason`
  - `next_action`
  - `compare_ready`
  - `iterate_ready`
- stage compare/iterate responses now also carry:
  - `guided_reference_readiness` for explicit goal/reference readiness
  - `assembled_target_scope` for explicit assembled-model targeting semantics
  - `truth_bundle` for correction-oriented contact/gap/alignment/overlap findings
  - `truth_followup` for loop-ready truth handoff items and focus pairs
  - `correction_candidates` for one ranked merged candidate list that preserves
    vision evidence, truth evidence, and bounded macro options without
    collapsing their source boundaries
- richer spatial state now also has separate read-only artifacts outside the
  default stage payload:
  - `scene_scope_graph(...)`
  - `scene_relation_graph(...)`
  - `scene_view_diagnostics(...)`
  - use those on demand when one correction step needs a fuller structural,
    pair-relation, or framing/occlusion picture than the bounded stage handoff
    should carry by default
- `reference_compare_current_view(...)` can now also emit compact
  `view_diagnostics_hints` when the active framing/occlusion state makes the
  current checkpoint a weak basis for the next correction step; the full
  view-space report still stays separate from the default compare payload
- `reference_iterate_stage_checkpoint(...)` now derives its loop-facing
  `correction_focus` from ranked `correction_candidates` when they are present,
  so deterministic truth-only findings can still reach the staged correction
  loop even before the later disposition-policy leaf changes
- `reference_iterate_stage_checkpoint(...)` now also lets high-priority
  deterministic truth findings move `loop_disposition` to
  `inspect_validate`, instead of waiting only for repeated vision focus
- mesh-pair truth now distinguishes mesh-surface gap/contact from coarse bbox
  touching when the bounded scene truth path can do so, which reduces false
  "contact passed" claims on visibly gapped rounded primitives
- truth-followup and ranked correction summaries now explicitly call out the
  common "bbox-touching but mesh surfaces still separated" case, so operator
  guidance and loop focus do not overclaim visual fit
- assembled creature collection/object-set scopes now avoid obviously
  accessory-first anchors such as ears or eyes when a more structural primary
  target is available later in the set
- assembled creature truth now also expands the guided-creature scope into one
  deterministic required seam set instead of only a narrow
  `primary_to_others` anchor walk when supported head/face/body/tail/limb
  names are present
- required creature seam checks now carry structured attachment semantics:
  - seam kind such as `head_body`, `tail_body`, `limb_body`, `face_head`, or
    `nose_snout`
  - attachment verdict such as `seated_contact`, `floating_gap`,
    `intersecting`, or `misaligned_attachment`
  - the preferred bounded repair family for that seam
- `truth_followup` and ranked `correction_candidates` now keep multiple failing
  required creature seams visible together, so one repaired local pair no
  longer implies that the assembled creature stage is globally acceptable
- embedded organic seams such as snout/head or nose/snout now favor
  `macro_attach_part_to_surface`, while segment/contact seams such as
  head/body, tail/body, and limb/body continue to favor
  `macro_align_part_with_contact`; generic overlap cleanup remains the fallback
  for non-attachment pairs
- vision `recommended_checks` now keep only canonical MCP tool ids; invented
  labels are dropped and a small alias map is normalized onto canonical names
- external compare-path diagnostics and `VisionAssistContract` payloads now
  expose the selected `vision_contract_profile`, so operator-visible failures
  can distinguish contract selection from transport/provider wiring
- hybrid-loop stage compare now also applies model-aware budget control:
  - trims pairwise truth scope when needed
  - trims ranked correction candidates when needed
  - records the decision in `budget_control`
  - uses runtime token/image limits plus a bounded model-name bias instead of
    one static expansion size
  - small-tier downgrades now key off explicit model tokens such as `-mini` or
    `2b` / `3b` / `4b`-class names, so Gemini model names are not downgraded
    by the `gemini`/`mini` substring collision
- hybrid-loop compare/iterate responses now also expose `refinement_route`,
  which classifies:
  - the current correction domain
  - the selected bounded refinement family
  - selector rationale and source signals
- hybrid-loop compare/iterate responses now also expose `refinement_handoff`
  as an explicit recommendation-only next-tool-family handoff
- current first-pass refinement families are:
  - `macro`
  - `modeling_mesh`
  - `sculpt_region`
  - `inspect_only`
- current product rule: `sculpt_region` can be recommended through
  `refinement_handoff`, but deterministic sculpt tools are still not part of
  the normal `llm-guided` build visibility by default
- request-bound attachment of `vision_assistant` to macro MCP reports when a
  `capture_bundle` exists
- macro report integration now also folds bounded vision-driven follow-ups back
  into `verification_recommended` when the vision result contains deterministic
  check hints or clear mismatch/correction signals

Current reference-selection behavior:

- prefer references targeting the current object and current target view
- otherwise prefer object-specific references
- otherwise fall back to generic references for the requested view
- otherwise fall back to generic session references

Current image-budget assumption:

- the default bounded runtime now assumes up to `8` images per request
- this leaves room for before/after capture sets plus a small number of
  goal-scoped reference images

Current capture-profile policy:

- default to `compact`
- promote to `rich` only when the configured image budget is large enough to
  hold the richer before/after bundle plus at least one reference image
- this profile selection now happens before bundle generation on macro MCP
  paths, so the generated `capture_bundle` already reflects the chosen profile

## Local Runtime Setup

The local `transformers_local` backend is intentionally optional.

Install the local vision runtime only when you want to run local VLMs:

```bash
poetry install --with vision --no-interaction
```

For Apple Silicon local testing, the repo also supports an optional
`mlx_local` path:

```bash
poetry install --with mlx --no-interaction
```

Practical note:

- some local multimodal processors also need `torchvision` at runtime
- the optional `vision` / `mlx` install groups include that dependency so
  local model loading does not fail on missing processor backends

Preliminary runtime status:

- `mlx_local` has now passed a real smoke test on a small cached/downloaded
  model path (`mlx-community/Qwen3-VL-2B-Instruct-4bit`)
- the backend can load the model and complete inference without crashing
- local prompt + parse-repair helpers now let the backend turn fenced/echo-like
  outputs into a bounded structured payload instead of failing immediately
- the parser now also repairs common local-model drift shapes:
  - single-summary outputs such as `{"comparison": "..."}`
  - unsupported label-map outputs such as `{"before": "...", "after": "..."}`
- output quality is still an open product problem: a successful smoke test does
  not yet mean the returned structured interpretation is trustworthy enough
- current practical result on the MLX smoke path after prompt/parse tightening:
  - `Qwen3-VL-4B-Instruct-4bit` now returns a usable `goal_summary` on the
    synthetic before/after/reference harness case and is now the more
    reasonable candidate for real local trials on Apple Silicon
  - `Qwen3-VL-2B-Instruct-4bit` can now return the full bounded shape on the
    same case, which makes it useful for smoke/dev testing, but it also shows
    a higher risk of overconfident issue/check generation that still needs
    evaluation scoring before we trust it on real work
- current blocker is no longer "runtime crash" but "quality and trust"

## Provider Notes

Current practical provider/model notes on this branch:

| Provider Path | Model / Family | Evidence Type | Contract Profile | Current Status | Notes |
|---|---|---|---|---|---|
| `mlx_local` | `mlx-community/Qwen3-VL-4B-Instruct-4bit` | Harness-ranked + repo tests | n/a | Recommended local baseline | Current repo-validated local baseline for bounded vision work. Strong on the real viewport squirrel scenarios and usable for staged reference-guided correction loops. |
| `openai_compatible_external` via OpenRouter | `x-ai/grok-4.20-multi-agent` | Harness-ranked / live branch validation | `generic_full` | Strong external candidate for iterative compare | Live branch validation shows this model returns full structured output on `reference_iterate_stage_checkpoint(...)` and produces actionable `correction_focus` / mismatch guidance. |
| `openai_compatible_external` via OpenRouter | `qwen/qwen3-vl-32b-instruct` | Harness-ranked smoke + operator-reported current-view compare | `generic_full` | Structured current-view compare observed; default still not promoted | The simple `macro_finish_form` smoke was weak, but one operator-reported `2026-04-07` `reference_compare_current_view(...)` squirrel run on `blender-ai-mcp-guided-docker-openrouter` returned a parseable structured payload with actionable mismatch lists. Keep this model off the default recommendation path until the same behavior is reproduced in harness-ranked or repo-tracked richer loop coverage; the reported output still showed quality caveats such as a truncated `next_corrections` item. |
| `openai_compatible_external` via OpenRouter | Google-family ids such as `gemma` / `gemini` / `learnlm` | Automated routing coverage | `google_family_compare` | Supported contract path; per-model ranking still pending | Transport stays on the OpenRouter branch, but staged compare/reference-guided checkpoint flows can now reuse the same narrow compare contract and near-JSON repair path as other Google-family runtimes. Do not promote one specific model from routing support alone; require harness evidence first. |
| `openai_compatible_external` via OpenRouter | `qwen/qwen-vl-plus` | Operator-reported | `generic_full` | Not recommended for structured stage loops | One operator-reported squirrel reconstruction run on `blender-ai-mcp-guided-docker-openrouter` returned prose instead of the required JSON envelope on stages 1-3 of `reference_iterate_stage_checkpoint(...)`, then returned valid JSON only on stage 4. Treat this model as unstable for structured assembled/reference-guided iterate loops and not suitable as a default recommendation. |
| `openai_compatible_external` via OpenRouter | `qwen-vl-max` | Operator-reported | `generic_full` | Operator-reported instability on richer assembled loops | One operator-reported `blender-ai-mcp-guided-docker-openrouter` squirrel run reported that later `reference_iterate_stage_checkpoint(...)` stages with a larger assembled multi-part target degraded into prose instead of the expected JSON payload, which surfaced as an orchestrator-side structured-output failure. Treat this model as unstable for richer assembled stage loops until the behavior is reproduced and ranked in the formal harness. |
| `openai_compatible_external` via Google AI Studio / Gemini | `gemini-3-flash-preview` | Harness-ranked + automated coverage | `google_family_compare` | Supported for staged compare | Google AI Studio / Gemini remains on its provider-specific transport branch, but now shares the same explicit Google-family compare contract model as OpenRouter-hosted Google-family ids. |

Interpretation:

- `mlx_local` remains the safest current default for local reference-driven work
- OpenRouter is worth keeping enabled; `x-ai/grok-4.20-multi-agent` is the current strongest external branch candidate for iterative compare loops
- Google-family compare behavior is now chosen by `vision_contract_profile`, not only by transport provider identity
- treat `Operator-reported` rows as anecdotal evidence, not as formal promotion evidence; they can record success or instability notes, but promote a model/provider combination only after harness-ranked or explicitly reproduced automated evidence
- `qwen/qwen3-vl-32b-instruct` is no longer only a smoke-failure datapoint on this branch, but its current evidence is still too thin for default promotion
- deterministic silhouette analysis now depends on `Pillow`, which is part of
  the main runtime dependency set so Docker images that install only `main`
  still keep this path available

## External Vision Contract Profiles

The external vision runtime now resolves one explicit `vision_contract_profile`
separately from the transport/provider path.

Current vocabulary:

- `generic_full`
  - full bounded JSON contract for general external vision use
- `google_family_compare`
  - narrow staged-compare contract plus near-JSON repair for compatible
    Google-family compare flows

Resolution precedence:

1. explicit `VISION_EXTERNAL_CONTRACT_PROFILE` override
2. deterministic model-family match on external model ids such as
   `gemma` / `gemini` / `learnlm`
3. provider default
   - current `google_ai_studio` default resolves to
     `google_family_compare`
4. fallback to `generic_full`

Important runtime note:

- `VISION_EXTERNAL_PROVIDER` still selects transport/provider wiring such as
  OpenRouter vs Google AI Studio
- `vision_contract_profile` selects prompt/schema/parser behavior
- `google_family_compare` only narrows reference-guided checkpoint / staged
  compare flows; non-checkpoint external requests still keep the full JSON
  contract even when the resolved profile is Google-family
- harness outputs, parser diagnostics, and `VisionAssistContract` payloads now
  expose the resolved `vision_contract_profile` so failures can be traced back
  to contract routing versus transport/provider issues

OpenRouter/Qwen hardening note:

- OpenRouter's official request docs distinguish:
  - `response_format={"type":"json_object"}` for JSON mode
  - `response_format={"type":"json_schema", ...}` for strict structured output
  - `provider.require_parameters=true` to force routing only through providers
    that support the requested parameters
  - optional `response-healing` plugin for automatic JSON repair
- Qwen's official OpenAI-compatible structured-output docs emphasize
  `response_format={"type":"json_object"}` plus an explicit `JSON` keyword in
  the prompt
- the runtime now uses that documented posture for Qwen-family OpenRouter
  models:
  - prefer `json_object`
  - require parameter-aware provider routing
  - enable OpenRouter response-healing by default

OpenAI/Azure strict structured-output note:

- OpenAI/Azure-style strict `response_format=json_schema` rejects schemas when
  an object has `properties` whose keys are not all listed in `required`
- the generic full vision schema therefore keeps every top-level property in
  `required`, and nested objects such as `likely_issues.items` and
  `recommended_checks.items` also require every declared property
- optional/low-confidence fields should be represented by nullable values or
  empty arrays, not by omitting keys from strict structured output
- OpenRouter-hosted OpenAI-family models such as `openai/gpt-*` now default to
  the narrower checkpoint compare contract, because the full generic contract
  is unnecessarily large for stage compare and can be truncated by small
  output budgets
- set `VISION_EXTERNAL_CONTRACT_PROFILE=generic_full` only when an operator
  explicitly wants the full response envelope and has confirmed the selected
  model/provider can return it reliably

Operator reporting rule before model promotion:

- if an operator reports instability, record:
  - provider path
  - exact model id
  - resolved `vision_contract_profile`
  - whether the failure happened on a simple checkpoint compare or a richer
    assembled stage loop
  - whether the issue has been reproduced in `scripts/vision_harness.py` or a
    repo-tracked automated test
- do not promote a model/provider combination from operator reports alone

## What Improved

Business-level summary of the recent quality gain:

- we stopped letting local models "pass" with empty structured success when
  they returned the wrong JSON shape
- we started giving local models an explicit output template and told them
  where to put the one useful sentence if they cannot fill everything
- we now repair common local-model drift shapes such as:
  - `{"comparison": "..."}`
  - `{"summary": "..."}`
  - `{"before": "...", "after": "...", "reference": "..."}`

Practical impact:

- `4B` no longer collapses into an empty success payload on the current smoke
  harness case
- `2B` is still weaker, but it now returns something that can be evaluated
  instead of just being discarded as parser noise

## Boundary Rules

The vision layer is not the truth source.

- vision interprets visible change
- the result contract now also carries `boundary_policy` so downstream clients
  can see that `next_corrections` and confidence are non-authoritative hints
- measure/assert tooling remains the correctness layer
- router policy remains the policy layer
- FastMCP platform controls discovery/visibility/public surface behavior

Use these docs together with:

- [Tool Layering Policy](../_MCP_SERVER/TOOL_LAYERING_POLICY.md)
- [Router / Runtime Responsibility Boundaries](../_ROUTER/RESPONSIBILITY_BOUNDARIES.md)
- [MCP Server Docs](../_MCP_SERVER/README.md)
- [TASK-121](../_TASKS/TASK-121_Goal_Aware_Vision_Assist_And_Reference_Context.md)
- [Multi-View Capture Plan](./MULTI_VIEW_CAPTURE_PLAN.md)

## Implementation Notes

Current code-level anchors:

- `server/adapters/mcp/vision/`
- `server/adapters/mcp/contracts/vision.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/areas/reference.py`
- `server/application/tool_handlers/macro_handler.py`

## Validation

Focused local validation for the current vision/runtime/capture/reference slice:

```bash
poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_vision_result_types.py tests/unit/adapters/mcp/test_vision_external_backend.py tests/unit/adapters/mcp/test_vision_local_backend.py tests/unit/adapters/mcp/test_vision_capture_bundle.py tests/unit/adapters/mcp/test_vision_capture_runtime.py tests/unit/adapters/mcp/test_vision_runner.py tests/unit/adapters/mcp/test_vision_macro_reporting.py tests/unit/adapters/mcp/test_vision_macro_mcp_integration.py tests/unit/adapters/mcp/test_vision_macro_reference_integration.py tests/unit/infrastructure/test_vision_di.py tests/unit/adapters/mcp/test_assistant_runner.py tests/unit/adapters/mcp/test_sampling_assistant_docs.py -q
```

## Debug Harness

The repo now includes a local comparison/debug script:

```bash
poetry run python scripts/vision_harness.py \
  --backend mlx_local \
  --golden-json tests/fixtures/vision_eval/synthetic_round_cutout/golden.json \
  --mlx-model mlx-community/Qwen3-VL-4B-Instruct-4bit
```

The harness is intended for:

- comparing `mlx_local`, `transformers_local`, and `openai_compatible_external`
- checking normalized outputs on the same deterministic bundle
- checking scored outputs on reusable repo-tracked golden scenarios
- recording raw-output diagnostics such as:
  - `container_shape`: `json`, `fenced_json`, `embedded_json`, `prose`
  - `payload_shape`: `contract`, `summary_alias`, `input_echo`, `label_map`, `unsupported_json`, `no_json`
  - `vision_contract_profile`: resolved external compare-contract selection
- catching prompt/parse failures before they are hidden inside a larger MCP flow

OpenRouter can now be used through the same `openai_compatible_external` path.

Minimal setup:

```bash
export VISION_ENABLED=1
export VISION_PROVIDER=openai_compatible_external
export VISION_EXTERNAL_PROVIDER=openrouter
export VISION_EXTERNAL_CONTRACT_PROFILE="google_family_compare"
export VISION_OPENROUTER_MODEL="google/gemma-3-27b-it:free"
export VISION_OPENROUTER_API_KEY_ENV=OPENROUTER_API_KEY
export OPENROUTER_API_KEY="<your-openrouter-key>"
export VISION_OPENROUTER_REQUIRE_PARAMETERS=true
export VISION_OPENROUTER_ENABLE_RESPONSE_HEALING=true
export VISION_OPENROUTER_PREFER_JSON_OBJECT_FOR_QWEN=true
```

Config precedence note:

- if `VISION_EXTERNAL_PROVIDER=openrouter`, the runtime uses the OpenRouter
  provider profile and default base URL
- model/auth values resolve from `VISION_OPENROUTER_*` first and then fall back
  to generic `VISION_EXTERNAL_*`
- if `VISION_EXTERNAL_CONTRACT_PROFILE` is unset, common Google-family model
  ids such as `gemma` or `gemini` auto-match to
  `google_family_compare`; the explicit env above keeps the compare-contract
  assumption visible in reproducible harness runs

Optional OpenRouter ranking headers:

```bash
export VISION_OPENROUTER_SITE_URL="https://example.com"
export VISION_OPENROUTER_SITE_NAME="blender-ai-mcp-dev"
```

Qwen-family OpenRouter note:

- when the selected OpenRouter model id looks like a Qwen family model, the
  runtime now prefers `response_format={"type":"json_object"}` instead of
  `json_schema`
- this follows the official Qwen structured-output guidance more closely while
  still keeping the repo's bounded JSON contract on the parsing side

Harness example:

```bash
poetry run python scripts/vision_harness.py \
  --backend openai_compatible_external \
  --external-provider openrouter \
  --external-contract-profile google_family_compare \
  --openrouter-model "google/gemma-3-27b-it:free" \
  --openrouter-api-key-env OPENROUTER_API_KEY \
  --golden-json tests/fixtures/vision_eval/squirrel_head_to_face_camera_perspective/golden.json
```

Google AI Studio / Gemini can now also be used through the same
`openai_compatible_external` path.

Minimal setup:

```bash
export VISION_ENABLED=1
export VISION_PROVIDER=openai_compatible_external
export VISION_EXTERNAL_PROVIDER=google_ai_studio
export VISION_EXTERNAL_CONTRACT_PROFILE="google_family_compare"
export VISION_GEMINI_MODEL="gemini-2.5-flash"
export VISION_GEMINI_API_KEY_ENV=GEMINI_API_KEY
export GEMINI_API_KEY="<your-google-ai-studio-key>"
```

Config precedence note:

- if `VISION_EXTERNAL_PROVIDER=google_ai_studio`, the runtime uses the Google
  AI Studio provider profile and default base URL
- model/auth values resolve from `VISION_GEMINI_*` first and then fall back to
  generic `VISION_EXTERNAL_*`
- `VISION_EXTERNAL_CONTRACT_PROFILE` is optional here because the provider
  default already resolves to `google_family_compare`, but keeping it explicit
  can help when reproducing compare-path evidence across harness runs

Harness example:

```bash
poetry run python scripts/vision_harness.py \
  --backend openai_compatible_external \
  --external-provider google_ai_studio \
  --external-contract-profile google_family_compare \
  --gemini-model "gemini-2.5-flash" \
  --gemini-api-key-env GEMINI_API_KEY \
  --golden-json tests/fixtures/vision_eval/squirrel_face_to_body_camera_perspective/golden.json
```

Opt-in real-model comparison for the new view-family variants:

```bash
RUN_REAL_VISION_MODEL_COMPARISON=1 poetry run pytest tests/e2e/vision/test_real_view_variant_model_comparison.py -q -m slow
```

Opt-in real reference-guided creature comparison:

```bash
RUN_REAL_REFERENCE_GUIDED_CREATURE_EVAL=1 \
VISION_REFERENCE_FRONT_PATH=/abs/path/squirrel-front.png \
VISION_REFERENCE_SIDE_PATH=/abs/path/squirrel-side.png \
poetry run pytest tests/e2e/vision/test_reference_guided_creature_comparison.py -q -m slow
```

Hybrid-loop regression guidance:

- `_docs/_VISION/HYBRID_LOOP_REAL_CREATURE_EVAL.md`
- `_docs/_VISION/REFERENCE_GUIDED_CREATURE_TEST_PROMPT.md`
- `_docs/_VISION/CROSS_DOMAIN_REFINEMENT_ROUTING_EVAL.md`
- use it to review the current staged creature loop in this order:
  - `loop_disposition`
  - `correction_candidates`
  - `truth_followup`
  - `action_hints`
  - `correction_focus`
  - `silhouette_analysis`
- keep the eval pack split between:
  - simpler checkpoint/compare-path reproduction
  - richer assembled loops using `target_objects=[...]` or
    `collection_name=...`, because model stability can diverge sharply between
    those two shapes

Current repo-tracked first-pass scenarios:

- `tests/fixtures/vision_eval/synthetic_round_cutout/`
- `tests/fixtures/vision_eval/synthetic_no_change/`
- `tests/fixtures/vision_eval/synthetic_reference_mismatch/`
- `tests/fixtures/vision_eval/default_cube_to_picnic_table/`
- `tests/fixtures/vision_eval/squirrel_head_to_face/`
- `tests/fixtures/vision_eval/squirrel_face_to_body/`
- `tests/fixtures/vision_eval/squirrel_head_to_body/`
- `tests/fixtures/vision_eval/squirrel_head_to_face_user_top/`
- `tests/fixtures/vision_eval/squirrel_face_to_body_user_top/`
- `tests/fixtures/vision_eval/squirrel_head_to_body_user_top/`
- `tests/fixtures/vision_eval/squirrel_head_to_face_camera_perspective/`
- `tests/fixtures/vision_eval/squirrel_face_to_body_camera_perspective/`
- `tests/fixtures/vision_eval/squirrel_head_to_body_camera_perspective/`

## First Scored Baseline

## Deterministic Silhouette Layer

The staged creature loop now has one deterministic silhouette-analysis layer on
top of the existing bounded vision/runtime baseline.

Current public payload additions on `reference_compare_stage_checkpoint(...)`
and `reference_iterate_stage_checkpoint(...)`:

- `silhouette_analysis`
  - typed metrics such as `mask_iou`, `contour_drift`, `aspect_ratio_delta`,
    `upper_band_width_delta`, `mid_band_width_delta`, `lower_band_width_delta`,
    `left_projection_delta`, and `right_projection_delta`
- `action_hints`
  - typed, bounded tool suggestions derived from those silhouette metrics
- `part_segmentation`
  - optional sidecar placeholder; defaults to `status="disabled"` on the
    normal runtime

Interpretation rules:

- silhouette metrics are perception evidence, not truth
- `action_hints` complement `correction_candidates` and `truth_followup`
- `vision_contract_profile` still only routes external prompt/schema/parser
  behavior; it is not itself evidence or proof that the result is correct

Current staged-loop reading order for creature work:

- `loop_disposition`
- `correction_candidates`
- `truth_followup`
- `action_hints`
- `correction_focus`
- `silhouette_analysis.metrics`
- `vision_assistant.result.shape_mismatches` / `proportion_mismatches`

## Optional Part-Segmentation Sidecar

Part-aware segmentation remains explicitly opt-in and separate from the
default vision runtime path.

Current config surface:

- `VISION_SEGMENTATION_ENABLED=false` by default
- `VISION_SEGMENTATION_PROVIDER=generic_sidecar`
- `VISION_SEGMENTATION_ENDPOINT`
- `VISION_SEGMENTATION_MODEL`
- `VISION_SEGMENTATION_API_KEY` / `VISION_SEGMENTATION_API_KEY_ENV`
- `VISION_SEGMENTATION_TIMEOUT_SECONDS`
- `VISION_SEGMENTATION_MAX_PARTS`

Boundary rules:

- the sidecar stays advisory-only
- failure or absence of the sidecar must not break normal guided sessions
- this config surface is separate from `VISION_EXTERNAL_CONTRACT_PROFILE`

Current first-pass scored baseline on the synthetic repo scenarios:

- `Qwen3-VL-4B-Instruct-4bit`
  - scored `strong` on `synthetic_round_cutout`
  - still weak on completeness there: it passed the direction/reference checks
    but returned no `visible_changes`
- `Qwen3-VL-2B-Instruct-4bit`
  - scored `strong` on `synthetic_round_cutout`
  - scored `strong` on `synthetic_no_change`
  - still needs caution on harder scenarios because it tends to produce richer
    issue/check output, which may be useful or may become overconfident on
    noisier real viewport bundles

Current first-pass real viewport smoke comparison on `default_cube_to_picnic_table`:

- `Qwen3-VL-4B-Instruct-4bit`
  - scored `strong`
  - produced a clean, concise summary that the default cube scene was replaced
    by a detailed picnic table model
  - produced useful `visible_changes`
  - produced no extra issues/checks on this easy smoke scenario
  - after the viewport-smoke heuristic update, this scenario now scores `1.0`
    and the direction classifier maps the replacement wording to `improved`
- `Qwen3-VL-2B-Instruct-4bit`
  - also scored `strong`
  - correctly recognized the large scene/object replacement
  - but added noisier `likely_issues` and `recommended_checks` that do not add
    much value on such an easy smoke case
  - still scores lower (`0.875`) because its wording on this case does not
    always hit the direction heuristic and it remains more prone to noisy
    follow-up output

Current interpretation of that comparison:

- both models can handle a large before/after scene replacement smoke case
- `4B` is the cleaner local baseline for real smoke usage
- `2B` remains more prone to overproducing analysis on easy cases
- the current scoring heuristic is improved for this scenario, but not fully
  generalized yet: `4B` now maps cleanly to `improved`, while `2B` still uses
  variant phrasing that the heuristic does not always classify correctly

Current first-pass real viewport progression comparison on the squirrel scenarios:

- `Qwen3-VL-4B-Instruct-4bit`
  - scored `1.0` / `strong` on:
    - `squirrel_head_to_face`
    - `squirrel_face_to_body`
    - `squirrel_head_to_body`
  - produced concise, clean progression summaries with useful `visible_changes`
- `Qwen3-VL-2B-Instruct-4bit`
  - also scored `1.0` / `strong` on the same three squirrel scenarios after the
    heuristic update
  - still tends to add noisier `likely_issues` and `recommended_checks` than
    `4B`, so the cleaner practical baseline remains `4B`

Additional repo-tracked real viewport variants now also exist for:

- direct top-down `USER_PERSPECTIVE` captures
- fixed named-camera perspective captures

Those variants mirror the same squirrel progression states so the harness can
compare whether the current logic stays stable across view families instead of
only one screenshot style.

First real-model comparison on those new view-family variants:

- `Qwen3-VL-2B-Instruct-4bit`
  - after the latest local prompt/parse cleanup, now stays `strong` on all 6
    new scenarios with `1.0` on all 6
  - current rerun on those 6 variants produced `0` `likely_issues` and `0`
    `recommended_checks`
- `Qwen3-VL-4B-Instruct-4bit`
  - after the latest direction-heuristic update, now also stays `strong` on all
    6 new scenarios with `1.0` on all 6
  - current rerun on those 6 variants produced `0` `likely_issues` and `0`
    `recommended_checks`

Current interpretation of that comparison:

- both models handle the new top-view and fixed-camera progression bundles
- the earlier scoring asymmetry on 4B's shorter phrasing is now fixed on those
  6 variants
- `4B` remains the safer practical local baseline, but the new 2B rerun is now
  materially cleaner than the earlier baseline and is more credible for
  lightweight smoke/dev use on this scenario family
  instead of treating extra issue/check output as neutral

Stability check:

- rerunning `default_cube_to_picnic_table` after the progression-heuristic
  update did not regress the earlier result
  - `4B`: still `1.0`
  - `2B`: still `0.875`

Practical reading of that baseline:

- first-pass synthetic scoring now works and is reusable
- current score alone is not enough to promote a model
- the next important differentiator is harder bundle coverage:
  - real macro captures
  - reference mismatch
  - richer/noisier multi-view cases
- one operator-reported OpenRouter `qwen/qwen-vl-plus` squirrel flow showed a
  stricter structured-output failure pattern: stages 1-3 returned prose
  instead of JSON on `reference_iterate_stage_checkpoint(...)`, while stage 4
  later returned valid JSON; that inconsistency is enough to keep it out of
  the recommended set for assembled reference loops
- one operator-reported OpenRouter `qwen-vl-max` run on a richer assembled
  squirrel flow already showed this failure class: stages 3/4 degraded into
  prose instead of structured JSON once more parts were present, which is a
  useful reminder that today's ranking still under-covers larger assembled
  stage loops
