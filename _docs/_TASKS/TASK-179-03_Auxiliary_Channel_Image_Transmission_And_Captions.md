# TASK-179-03: Auxiliary-Channel Image Transmission And Captions

**Parent:** [TASK-179](./TASK-179_Blender_Depth_Normal_And_Object_ID_Auxiliary_Passes.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Follow-on After:** [TASK-179-01](./TASK-179-01_Addon_Object_ID_Depth_And_Normal_Render_Passes.md), [TASK-174](./TASK-174_Per_Image_Caption_Interleaving_For_Vision_Payloads.md)
**Objective:** Transmit the depth, normal, and object-ID renders to the VLM as labeled auxiliary captures (new `view_kind` values), captioned per TASK-174, with budget-aware inclusion and explicit advisory framing. The auxiliary captures flow through the existing capture orchestration and transport without breaking the flat IMAGES roster, the image budget, or the external payload contract.
**Repository Touchpoints:** `server/adapters/mcp/vision/capture_runtime.py`, `server/adapters/mcp/vision/capture.py`, `server/adapters/mcp/contracts/vision.py`, `server/adapters/mcp/vision/prompting.py`, `server/adapters/mcp/vision/config.py`, `server/adapters/mcp/vision/runner.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/e2e/vision/test_external_contract_profile_compare_path.py`
**Acceptance Criteria:**
- `VisionCaptureImageContract.view_kind` (`server/adapters/mcp/contracts/vision.py:22`) gains auxiliary kinds (e.g. `"depth"`, `"normal"`, `"object_id"`) so auxiliary renders are typed distinctly from `wide` / `focus` / `overlay` / `reference`
- `capture_runtime.py` can append auxiliary captures for a canonical view from the TASK-179-01 geometry-pass call, with deterministic labels and reversible scene handling, without changing the default `SOLID` view-set
- each auxiliary image carries a caption (per TASK-174) that names the channel and states it is advisory geometric enrichment, not authoritative measurement
- including auxiliary captures is **budget-aware**: the request never exceeds `effective_max_images`, so `runner.py:170` still accepts it; when the budget is tight, auxiliary captures are dropped before primary captures and the drop is reported
- the external payload (`prompting.py` flat IMAGES roster) and the external contract profile path stay valid with auxiliary captures present

## Implementation Notes

- Transport today is caption-blind and flat: `capture.py:_capture_to_image_input`
  (`:20-30`) maps each `VisionCaptureImageContract` to a bare `VisionImageInput`
  with only `label` + `media_type`; the prompt's flat `IMAGES:` roster
  (`server/adapters/mcp/vision/prompting.py:~497/511`) lists images without
  per-image captions, and the backends append images as bare blobs. TASK-174 owns
  the per-image caption interleaving; this slice depends on it to attach an
  advisory caption to each auxiliary render. Until TASK-174 lands, this slice can
  still type and route auxiliary captures, but the caption text must be wired
  through the TASK-174 mechanism rather than duplicated here.
- New `view_kind` values: extend the `Literal` on
  `VisionCaptureImageContract.view_kind` (`contracts/vision.py:22`) to include
  the auxiliary kinds. `view_kind` is consumed by selection logic such as
  `reference_silhouette.py:select_silhouette_analysis_capture(...)` (which keys
  on `view_kind == "focus"`), so auxiliary kinds must be additive and must not be
  picked up by the silhouette focus-view selection.
- Capture append path: in
  `server/adapters/mcp/vision/capture_runtime.py:capture_stage_images(...)`,
  after the canonical focus view is rendered, optionally call the new
  geometry-pass RPC (TASK-179-01) and write the returned depth/normal/object-ID
  base64 to viewport output paths via `get_viewport_output_paths`, appending
  `VisionCaptureImageContract`s with the new `view_kind` and a deterministic
  label (e.g. `f"{preset.name}_{stage}_depth"`). Keep the existing reversible
  `capture_scene_state` / `restore_scene_state` discipline (`capture_runtime.py:199/260`).
- Budget: the image cap is `VisionRuntimeConfig.max_images` (default 8,
  `config.py:121`), clipped by `VISION_FAIL_SAFE_MAX_IMAGES` = 12
  (`config.py:28`, `effective_max_images` at `config.py:133`), and
  `runner.py:170` rejects requests over `effective_max_images`. Auxiliary
  captures must therefore be added under a budget check and be the **first** to be
  dropped when the budget is tight; report which auxiliary captures were dropped
  so the orchestrator knows the evidence was budget-limited rather than missing.
- Advisory framing in the caption is mandatory: the caption must mark the channel
  as advisory geometric enrichment (`not_truth_source`), and depth must be framed
  as relative, never an absolute measurement. Do not emit raw depth values or
  coordinate tokens as primary text; the image plus a short symbolic caption is
  the signal.
- Research basis (cite, do not implement VLM chain-of-thought): the value of
  shipping depth/normal as explicit channels is motivated by SpatialRGPT
  (arXiv:2406.01584), SD-VLM depth encoding +26.9 pts (arXiv:2509.17664), the
  spatial-reasoning survey treating depth as a standard channel
  (arXiv:2405.10255), and normal-map passes in GPTEval3D / 3DGen-Bench
  (arXiv:2401.04092 / arXiv:2503.21745). Captions stay short and symbolic;
  spatial reasoning stays in the orchestrator, not the VLM prompt.

## Pseudocode

```python
def append_auxiliary_captures(captures, scene_handler, preset, stage, bundle_id, *, budget_remaining):
    if budget_remaining <= 0 or not preset.emit_geometry_passes:
        return captures, []
    passes = scene_handler.get_geometry_passes(
        target_objects=preset.target_objects, include_normal=preset.include_normal
    )
    if not passes.get("available"):
        return captures, [f"geometry_passes_unavailable:{passes.get('reason')}"]

    appended, dropped = [], []
    for kind, b64 in (("object_id", passes["object_id_image_b64"]),
                      ("depth", passes["depth_image_b64"]),
                      ("normal", passes.get("normal_image_b64"))):
        if b64 is None:
            continue
        if len(appended) >= budget_remaining:
            dropped.append(kind)              # budget-aware: aux dropped before primary
            continue
        path = write_viewport_output(f"{bundle_id}_{stage}_{preset.name}_{kind}.png", b64)
        appended.append(VisionCaptureImageContract(
            label=f"{preset.name}_{stage}_{kind}",
            image_path=str(path), preset_name=preset.name,
            media_type="image/png", view_kind=kind,   # new auxiliary view_kind
        ))
    return captures + appended, dropped
```

## Runtime / Security Contract Notes

- Auxiliary depth/normal/object-ID captures are **advisory enrichment**: they
  cannot mark a gate complete or unlock a tool, and their captions must state
  `not_truth_source` / `requires_deterministic_checks_for_correctness`.
- Depth captions describe **relative** depth only; no absolute measurement.
  Any magnitude in surrounding evidence stays a proportional ratio against a
  trusted reference anchor.
- The captions are symbolic and short — no raw coordinate tokens as primary
  evidence, and no VLM-side chain-of-thought for spatial judgments.
- Budget-safety is a hard contract: auxiliary inclusion must never push the
  request past `effective_max_images`; if it would, auxiliary captures are dropped
  first and the drop is reported.
- All capture-time scene mutation stays reversible and main-thread-safe via the
  existing `capture_scene_state` / `restore_scene_state` flow.

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/e2e/vision/test_external_contract_profile_compare_path.py`
- a focused unit lane asserting: new `view_kind` round-trips through
  `VisionCaptureImageContract`; auxiliary captures are appended only within
  budget; budget-tight runs drop auxiliary captures first and report the drop;
  silhouette focus-view selection does not pick up auxiliary kinds

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Status / Board Update

- board tracking remains on umbrella `TASK-179`
- no separate promoted board-row change is expected for this subtask unless it
  later becomes a standalone follow-on

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_external_contract_profile_compare_path.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`

## Validation Category

- auxiliary-channel transport + caption + budget proof
