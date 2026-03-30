# Vision Layer Docs

Working documentation for the `TASK-121` vision-assist layer.

This folder is the canonical place to describe:

- pluggable vision backend strategy (`transformers_local` / `openai_compatible_external`)
- request-bound runtime behavior
- deterministic capture-bundle inputs
- goal-scoped reference image context
- macro/workflow integration of `capture_bundle` and `vision_assistant`
- evaluation constraints and model-comparison notes

## Current State

The repo now has the first implementation scaffolding for the vision layer:

- lazy, optional vision runtime config and backend resolution
- local and external backend families
- bounded `VisionAssistContract` / `VisionAssistantContract`
- richer optional result semantics for later correction loops:
  - `shape_mismatches`
  - `proportion_mismatches`
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
- bounded `reference_compare_checkpoint(...)` surface for comparing one current
  stage/checkpoint image against the active goal plus attached references
- bounded `reference_compare_current_view(...)` surface for capture-then-compare
  on the current viewport/camera path during staged manual work
- bounded `reference_compare_stage_checkpoint(...)` surface for deterministic
  multi-view stage capture + compare during staged manual/reference-guided work
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
- catching prompt/parse failures before they are hidden inside a larger MCP flow

Opt-in real-model comparison for the new view-family variants:

```bash
RUN_REAL_VISION_MODEL_COMPARISON=1 poetry run pytest tests/e2e/vision/test_real_view_variant_model_comparison.py -q -m slow
```

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
