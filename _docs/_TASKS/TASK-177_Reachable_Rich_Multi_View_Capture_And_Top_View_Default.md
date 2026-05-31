# TASK-177: Reachable Rich Multi-View Capture And Top-View Default

**Status:** ✅ Done
**Progress:** Completed 2026-05-31. TASK-177-01 (budget-aware best-N capture view selection substrate) shipped 2026-05-30 via changelog 371. TASK-177-03 is fully wired by changelogs 384 and 389: `VISION_CAPTURE_GRID_ENABLED`, runtime config, `view_kind="grid"`, per-image captions, and stage/packet transmission. TASK-177-02 closed 2026-05-31: compact staged capture now includes orthographic `target_top` and perspective `target_oblique_left` with symbolic projection metadata.
**Priority:** 🟡 Medium
**Category:** Vision / Multi-View Capture
**Estimated Effort:** Medium
**Follow-on After:** [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md)
**Related:** [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md), [TASK-173](./TASK-173_Reference_Guided_Creature_Scope_Convergence_And_Optional_Grounding_Followups.md), [_docs/_VISION/MULTI_VIEW_CAPTURE_PLAN.md](../_VISION/MULTI_VIEW_CAPTURE_PLAN.md)

## Relationship To Existing Board Items

- `TASK-172` already shipped the optional vision-capability runtime and the
  default-off optional-runtime seam. This family is a separate, standalone
  umbrella that consumes that runtime posture without reopening it; it does not
  add new heavy perception sidecars and does not re-touch the provider-capability
  substrate owned by `TASK-140-06` / `TASK-172`.
- `TASK-166` owns hierarchical compare, perceived-evidence budgeting, and the
  configurable vision-assist input budgets. This family lives upstream of compare
  arbitration: it changes which deterministic capture views are produced and how
  the best-N are selected within the existing image budget, then hands the same
  bundle contract downstream. It does not change compare schema arbitration.
- `TASK-173` is a creature-loop consumer follow-on. This family is generic
  (any reference-guided target, not creature-only) and only improves the
  underlying capture view-set that `TASK-173` and every other compare path read.
- `_docs/_VISION/MULTI_VIEW_CAPTURE_PLAN.md` already documents an aspirational
  8-image long-term bundle (`context_wide`, `target_focus`, oblique left/right,
  front/side/top, `target_detail`). The shipped runtime cannot reach that set
  under default config, so this family also reconciles that plan with reality.

## Objective

Make the rich, multi-angle capture set actually reachable under the default
runtime, add an orthographic top/overhead view to the default compact bundle,
and select the best-N views within the effective image budget instead of letting
the preset-gate arithmetic silently force the compact triad. The result should
be deterministic capture coverage that is genuinely useful for 3D-scene
understanding (depth, roundness, overhang, relative distance) while staying
inside the existing bounded image budget and advisory-vision boundary.

## Business Problem

The rich 8-view capture preset is unreachable under default configuration, so
only the compact triad ever ships, and the compact triad alone makes 3D shape
ambiguous:

- `server/adapters/mcp/vision/policy.py:13-25` (`choose_capture_preset_profile`)
  only returns `"rich"` when `max_images >= 8 * 2 + max(1, reference_image_count)`,
  i.e. at least `16 + references` images.
- `server/infrastructure/config.py:59` defaults `VISION_MAX_IMAGES` to `8`, and
  `server/adapters/mcp/vision/config.py:121` defaults the runtime
  `max_images` field to `8`.
- `server/adapters/mcp/vision/config.py:28` / `:136` fail-safe-clip the effective
  image cap to `VISION_FAIL_SAFE_MAX_IMAGES = 12` via `effective_max_images`.
- `server/adapters/mcp/vision/runner.py:170-179` rejects any request whose image
  count exceeds `runtime.effective_max_images` with
  `rejection_reason="image_budget_exceeded"`.

So under default config the rich profile gate (>= 16 + references) can never be
satisfied while the effective cap is 12, and even if a user raised
`VISION_MAX_IMAGES` the rich profile produces `8 presets * 2 stages = 16` capture
contracts that the runner would reject. The practical outcome is that only
`COMPACT_CAPTURE_PRESET_SPECS` (`context_wide`, `target_front`, `target_side`,
`target_top` in `capture_runtime.py:48-87`) ever ships, dropping the oblique 3/4
and detail angles. An orthographic triad alone leaves depth, roundness, and
overhang ambiguous; the current compact triad also has no oblique view at all.

Separately, while the compact preset already includes `target_top`, the project
does not treat an explicit top-down/overhead view as a first-class, always-present
default, and `_docs/_VISION/MULTI_VIEW_CAPTURE_PLAN.md` still advertises an
8-image bundle that the runtime cannot produce.

## Business Outcome

After this umbrella lands:

- the capture layer captures a richer candidate view-set and then selects the
  best-N within the *effective* image budget, so a more informative bundle ships
  without raising the fail-safe caps or bypassing the runner budget check
- an orthographic top/overhead view is a guaranteed member of the default
  bundle, and an oblique 3/4 view is added when the budget allows, capped at
  roughly 6-8 transmitted views
- selection is deterministic and auditable, with view-kind / projection metadata
  recorded so the downstream VLM and orchestrator know what each view is
- optionally, the selected views can be composited into one labeled grid image
  for models/budgets where a single annotated montage outperforms many separate
  images, behind a default-off config flag
- `_docs/_VISION/MULTI_VIEW_CAPTURE_PLAN.md` matches what actually ships

## Non-Goals

- Vision stays **advisory**: any view-set, selection metadata, projection hint,
  or grid composite produced here is still VLM-facing input or VLM interpretation
  and must keep `not_truth_source` / `requires_deterministic_checks_for_correctness`
  posture. Deterministic inspection / assertion / silhouette continue to own
  scene truth. Capture selection must not mark gates complete or unlock tools.
- Any magnitude the bundle or downstream evidence surfaces is a **proportional
  ratio vs a trusted reference anchor**, never an authoritative absolute
  measurement (VLMs land within 2x on only ~37% of metric tasks).
- Do not turn on heavier perception sidecars (SAM / SAM2 / GroundingDINO /
  Depth-Anything / CLIP / DINO embeddings) here. They stay default-off,
  advisory-only, and packet-bounded under the `TASK-172` optional-runtime seam,
  and this family does not reopen the `TASK-140-06` provider-capability substrate.
- Do not emit raw coordinate tokens as primary evidence; prefer symbolic
  view-kind / projection labels and proportional ratios, with coordinates on
  demand only (raw-coordinate primacy hurts LLM spatial reasoning).
- Do not add VLM-side chain-of-thought for spatial judgments; reasoning stays in
  the orchestrator.
- Do not raise the fail-safe budget caps or bypass the runner image-budget
  rejection; the whole point is to select within the existing budget.
- Do not introduce persistent helper-camera rigs as the default capture path;
  keep reversible viewport/view-state manipulation per
  `_docs/_VISION/MULTI_VIEW_CAPTURE_PLAN.md`.

## Execution Structure

| Order | Task | Purpose |
|------|------|---------|
| 1 | [TASK-177-01](./TASK-177-01_Decouple_Capture_From_Transmission_And_Budget_Aware_Selection.md) | Decouple Capture From Transmission And Budget-Aware Selection |
| 2 | [TASK-177-02](./TASK-177-02_Orthographic_Top_And_Oblique_Default_Capture_Presets.md) | Orthographic Top And Oblique Default Capture Presets |
| 3 | [TASK-177-03](./TASK-177-03_Optional_Labeled_Multi_View_Grid_Composite.md) | Optional Labeled Multi-View Grid Composite |

## Repository Touchpoints

| Path / Module | Expected Ownership | Why It Is In Scope |
|---------------|--------------------|--------------------|
| `server/adapters/mcp/vision/policy.py` | capture-profile selection policy | `choose_capture_preset_profile` (`:13-25`) is the unreachable rich gate; capture-vs-transmit decoupling and budget-aware selection start here |
| `server/adapters/mcp/vision/runner.py` | bounded request runner | the image-budget rejection at `:170-179` must keep guarding transmission while selection runs before it |
| `server/adapters/mcp/vision/capture_runtime.py` | deterministic capture orchestration and preset specs | `CapturePresetSpec`, `COMPACT_/RICH_CAPTURE_PRESET_SPECS`, `capture_stage_images` own which views are captured and labeled |
| `server/adapters/mcp/vision/config.py` | runtime config and fail-safe caps | `effective_max_images` (`:132-136`) and the new selection/grid flags live here without raising fail-safe caps |
| `server/infrastructure/config.py` | env-backed runtime config | `VISION_MAX_IMAGES` default (`:59`) and any new selection/grid env keys |
| `server/adapters/mcp/vision/capture.py` | capture-to-request assembly | `build_vision_request_from_capture_bundle` / `build_vision_request_from_stage_captures` consume the selected captures and any grid composite |
| `server/adapters/mcp/contracts/vision.py` | capture contracts | `VisionCaptureImageContract.view_kind` and bundle preset metadata may need a top/oblique/grid view-kind and projection hint |
| `blender_addon/application/handlers/scene_viewport_mixin.py` | addon viewport RPC | `set_standard_view` (`:1081`, supports `FRONT|RIGHT|TOP`), `camera_orbit`, `get_viewport` are the reversible atomics for top/oblique capture; both RPC sides stay in sync |

## Test Matrix

| Slice | Primary Validation Lane | Why |
|------|--------------------------|-----|
| capture-vs-transmit decoupling and budget-aware selection | `tests/unit/adapters/mcp/test_vision_policy.py`, `tests/unit/adapters/mcp/test_vision_runtime_config.py`, `tests/unit/adapters/mcp/test_vision_capture_runtime.py`, `tests/unit/adapters/mcp/test_reference_images.py` | the unreachable rich gate, fail-safe caps, and runner budget rejection are exercised in these unit lanes |
| orthographic top + oblique default presets | `tests/unit/adapters/mcp/test_vision_capture_runtime.py`, `tests/unit/adapters/mcp/test_vision_capture_bundle.py`, `tests/e2e/vision/test_real_view_variant_model_comparison.py` | preset view sets and view-kind metadata are deterministic and proved against real viewport variants |
| optional labeled grid composite | `tests/unit/adapters/mcp/test_vision_runtime_config.py`, `tests/unit/adapters/mcp/test_vision_capture_runtime.py`, `tests/unit/adapters/mcp/test_vision_capture_bundle.py` | the grid flag default-off behavior and one-image-vs-many path are unit-provable |

## Acceptance Criteria

- under default config (`VISION_MAX_IMAGES=8`), a richer candidate view-set is
  captured and the transmitted bundle still respects `effective_max_images` and
  is never rejected by `runner.py:170-179` for `image_budget_exceeded`
- when only after-captures ship, best-N selection thresholds against a
  single-stage budget of 8 rather than the doubled `8 * 2` rich-bundle arithmetic
- the default transmitted bundle always contains an orthographic top/overhead
  view and, when budget allows, at least one oblique 3/4 view, capped at roughly
  6-8 transmitted views
- each transmitted capture carries deterministic view-kind / projection metadata
  so the downstream VLM and orchestrator can tell wide / focus / top / oblique /
  grid apart without parsing raw coordinates
- the optional labeled grid composite is default-off; when enabled it produces
  one annotated montage that respects the same bounded budget and stays advisory
- `_docs/_VISION/MULTI_VIEW_CAPTURE_PLAN.md` describes the bundle that actually
  ships, not an unreachable aspirational set
- vision output from this path keeps `not_truth_source` /
  `requires_deterministic_checks_for_correctness` and does not gate or unlock
- RESEARCH CAVEAT: the cited benchmarks (DiffuRank, VSI-Bench, GPT4Scene,
  IG-VLM, Orient Anything) are indoor-scan / synthetic / video-QA settings, not
  Blender-vs-reference comparison. Re-measure absolute gains on
  `tests/fixtures/vision_eval` golden fixtures before promoting any selection,
  top-view, or grid behavior past planning.

## Docs To Update

- `_docs/_TASKS/README.md`
- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_VISION/MULTI_VIEW_CAPTURE_PLAN.md`

## Tests To Add/Update

- split across the execution slices below; each child task owns its exact lane

## Changelog Impact

- completed through changelogs 371, 384, 389, and 393

## Status / Board Update

- `_docs/_TASKS/README.md` tracks `TASK-177` as a selected completed milestone
  on the Vision / Hybrid Loop lane
- child tasks remain nested historical slices and are all closed

## Validation Commands

- `git diff --check`
- `rg -n "TASK-177|Reachable Rich Multi-View Capture And Top-View Default|Decouple Capture From Transmission|Orthographic Top And Oblique Default Capture Presets|Optional Labeled Multi-View Grid Composite" _docs/_TASKS/TASK-177*.md`

## Validation Category

- planning / governance / task-family definition
