# TASK-179: Blender Depth, Normal And Object-ID Auxiliary Passes

**Status:** ✅ Done
**Progress:** Completed 2026-05-31. TASK-179-01 addon depth/object-ID/normal render passes shipped via changelogs 386-388. TASK-179-02 now has the object-ID index-map IoU helper, `ISceneTool` pass-method surface, support-evidence projection substrate from changelog 389, live staged-compare population via an internal `object_id_artifact` sidecar from changelog 390, and the 2026-05-31 fixture-calibrated per-object IoU threshold closeout. TASK-179-03 shipped the default-off depth/normal/object-ID auxiliary-channel transmission/caption path via changelog 391.
**Priority:** 🔴 High
**Category:** Vision / Geometric Evidence (Addon Render)
**Estimated Effort:** Large
**Follow-on After:** [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md), [TASK-173](./TASK-173_Reference_Guided_Creature_Scope_Convergence_And_Optional_Grounding_Followups.md)
**Related:** [TASK-174](./TASK-174_Per_Image_Caption_Interleaving_For_Vision_Payloads.md), [TASK-180](./TASK-180_Set_Of_Mark_Object_Bound_Visual_Marks.md), [TASK-183](./TASK-183_Capability_Enriched_Vision_Schema_And_Deterministic_Cross_Check.md)

## Audit Follow-on Note

`TASK-179` remains closed. The June 2026 Vision 3D understanding audit found
follow-up work around object-ID contract precision and depth caption encoding;
that work is tracked as standalone follow-on [TASK-184](./TASK-184_Vision_3D_Understanding_Audit_Corrections.md)
instead of reopening this completed umbrella.

2026-06-22 TASK-184 closeout: object-ID contracts now explicitly describe
Object Index / `pass_index` evidence as whole-object visible-surface support,
carry grayscale-band/object-count/fragmentation diagnostics, and keep
Cryptomatte deferred. Relative-depth captions now include
`encoding=near_bright_far_dark`.

## Relationship To Existing Board Items

- `TASK-172` already shipped the optional-runtime seam for heavy perception
  sidecars (classifier / localization / segmentation) as default-off, advisory,
  packet-bounded capabilities. This family does **not** reopen that substrate; it
  adds first-party deterministic Blender render passes that need no external
  model, plus one strictly optional monocular-depth hook for the *reference*
  image that reuses the existing TASK-172 default-off sidecar boundary.
- `TASK-173` (🚧 In Progress) targets creature-scope convergence, but even
  there the deterministic evidence path remains single-view 2D silhouette only. Two solids that share a
  silhouette can read as a 3D match because the loop is blind to depth,
  concavity, occlusion, and volume. This family supplies the geometric channels
  that make per-part and depth-aware evidence possible.
- This umbrella is a **standalone** new family. It links its upstream parents via
  **Follow-on After:** and sibling recommendations via **Related:**; it does not
  use **Parent:** for those, since they are separate families. Only the three
  subtasks below use **Parent:** pointing at this umbrella.

## Objective

Give the deterministic evidence path real geometric channels for canonical
target views without invoking any external model:

- add an addon-side compositor / render-pass path that emits a deterministic
  **object-ID mask image**, a **Z-depth image**, and an optional **normal image**
  for the active camera/view, wired through RPC on both sides and fully reversible
- use the deterministic object-ID masks to compute **per-object mask IoU** in
  `silhouette.py` so geometric mismatch can be attributed to a specific
  registered part instead of only a whole-frame silhouette
- transmit depth / normal / object-ID renders to the VLM as **labeled auxiliary
  captures** (new `view_kind` values), captioned per TASK-174, with budget-aware
  inclusion and explicit advisory framing
- keep all of this advisory: the new channels enrich evidence and per-part
  attribution, but deterministic inspection / assertion / silhouette still own
  scene truth, and vision still cannot mark gates complete or unlock tools.

## Business Problem

Every capture preset hardcodes `shading="SOLID"` even though the underlying
viewport API supports other modes:

- `server/adapters/mcp/vision/capture_runtime.py:30` sets `shading: str = "SOLID"`
  on `CapturePresetSpec`, and every preset in `COMPACT_CAPTURE_PRESET_SPECS` /
  `RICH_CAPTURE_PRESET_SPECS` repeats `shading="SOLID"`; the addon
  `get_viewport(...)` in
  `blender_addon/application/handlers/scene_viewport_mixin.py:15` already
  validates `{"WIREFRAME", "SOLID", "MATERIAL", "RENDERED"}` and can produce
  other channels, but no caller asks for anything but flat solid color.
- All deterministic geometric evidence is single-view 2D silhouette:
  `server/adapters/mcp/vision/silhouette.py` extracts one whole-frame mask
  (alpha or Otsu largest component) and computes whole-frame `mask_iou`,
  `contour_drift`, `aspect_ratio_delta`, and uncalibrated magic-number band
  metrics (`high=0.35` for `mask_iou`). It is blind to depth, concavity,
  occlusion ordering, and volume, so two different solids that share a silhouette
  can be read as a 3D match, and a mismatch can never be attributed to a specific
  registered part.
- The capture path swallows camera-op failures (`except Exception: pass` at
  `capture_runtime.py:211/216/221/232`) and labels images by
  `f"{preset.name}_{stage}"` (`capture_runtime.py:251`) with `view_kind`
  restricted to `Literal["wide", "focus", "overlay", "reference"]`
  (`server/adapters/mcp/contracts/vision.py:22`). There is no channel for an
  auxiliary geometric render, so even if the addon produced one it could not be
  typed, labeled, or routed.

Blender can emit depth / normal / object-index passes for the *same* camera
essentially for free, and an object-index (Object Index / `pass_index`)
compositor pass yields deterministic per-object masks **without SAM**. The repo
already has typed surfaces for part-aware evidence. As of changelog 390, staged
compare can now populate capture-side object-ID IoU in
`ReferenceSilhouetteAnalysisContract.per_object_metrics` from a deterministic
first-party pass. As of changelog 391, the same focus-view framing can also
transmit default-off depth/normal/object-ID auxiliary images to the VLM with
advisory captions and budget-drop metadata.

## Business Outcome

After this umbrella lands:

- a canonical target view can carry a deterministic object-ID mask, a Z-depth
  image, and an optional normal image, all reversible and main-thread-safe
- geometric mismatch can be attributed to a specific registered part via
  per-object mask IoU, instead of only a whole-frame silhouette score
- depth / normal / object-ID renders reach the VLM as clearly labeled,
  captioned auxiliary captures that the orchestrator can reason over, with the
  image budget respected and the advisory framing explicit in the caption
- two solids that share a silhouette can still be separated, because depth and
  per-part IoU evidence now exists for the orchestrator to act on
- the per-object masks become a reusable substrate for numbered visual marks
  (TASK-180) without re-running any external segmentation model.

## Non-Goals

- **Vision stays advisory.** The new depth / normal / object-ID channels are
  enrichment for VLM interpretation, not authority. All vision-derived structured
  fields keep `not_truth_source` / `requires_deterministic_checks_for_correctness`
  framing. Deterministic inspection, assertion, and silhouette own scene truth.
  Vision must not mark gates complete or unlock tools.
- **No authoritative absolute magnitudes.** Any magnitude surfaced from these
  channels is a **proportional ratio against a trusted reference anchor**, never
  an authoritative absolute measurement (VLMs are ~37% within 2x on metric
  tasks). Depth values are relative/normalized, not metric truth.
- **Heavy perception sidecars stay default-off.** The optional monocular-depth
  hook for the *reference* image reuses the TASK-172 optional-runtime seam:
  default-off, advisory-only, packet-bounded. Do **not** reopen the TASK-140-06
  provider-capability substrate, and do **not** make depth/normal estimation
  models default-on.
- **No raw coordinate tokens as primary evidence.** Per-part evidence is emitted
  as symbolic relations plus ratios (and per-object IoU); raw box/coordinate
  tokens are available on demand only, never as the primary spatial signal
  (3DGraphLLM 50.1->42.6; Text-Scene relations 59.4 vs coords 18.4).
- **No VLM-side chain-of-thought for spatial judgments** (VSI-Bench regression
  -1..-21%). The new channels feed the orchestrator; spatial reasoning stays in
  the orchestrator, not in the VLM prompt.
- do not replace the existing whole-frame silhouette metrics; per-object IoU is
  additive evidence alongside them.
- do not make the object-ID / depth / normal passes mandatory for every preset;
  they are opt-in canonical-view auxiliaries that must respect the image budget.

## Execution Structure

| Order | Task | Purpose |
|------|------|---------|
| 1 | [TASK-179-01](./TASK-179-01_Addon_Object_ID_Depth_And_Normal_Render_Passes.md) | Addon Object-ID, Depth And Normal Render Passes |
| 2 | [TASK-179-02](./TASK-179-02_Per_Object_Mask_IoU_In_Silhouette_Evidence.md) | Per-Object Mask IoU In Silhouette Evidence |
| 3 | [TASK-179-03](./TASK-179-03_Auxiliary_Channel_Image_Transmission_And_Captions.md) | Auxiliary-Channel Image Transmission And Captions |

## Repository Touchpoints

| Path / Module | Expected Ownership | Why It Is In Scope |
|---------------|--------------------|--------------------|
| `blender_addon/application/handlers/scene_viewport_mixin.py`, `blender_addon/application/handlers/scene.py`, `blender_addon/infrastructure/rpc_server.py`, `blender_addon/__init__.py` | addon render-pass producer + RPC registration | `get_viewport(...)` (`scene_viewport_mixin.py:15`) already validates shading and reverses state; a new reversible compositor/pass path for object-ID/depth/normal lives here, and `__init__.py` registers the new `scene.*` RPC method |
| `server/application/tool_handlers/scene_handler.py`, `server/adapters/rpc/client.py`, `server/domain/tools/scene.py`, `server/domain/interfaces/rpc.py` | server RPC mirror | `scene_handler.py:44-70` mirrors `scene.get_viewport`; the new pass method needs the matching server-side RPC call so both RPC sides stay in parity |
| `server/adapters/mcp/vision/capture_runtime.py`, `server/adapters/mcp/vision/capture.py` | capture orchestration | `CapturePresetSpec.shading` (`:30`), the swallowed camera-op failures (`:211/216/221/232`), the label format (`:251`), and `view_kind` routing live here; auxiliary captures and reversible state belong in this orchestration |
| `server/adapters/mcp/vision/silhouette.py`, `server/adapters/mcp/areas/reference_silhouette.py` | deterministic geometric evidence | `silhouette.py` whole-frame IoU (`:233-256`) is extended with deterministic per-object mask IoU sourced from the object-ID pass; `reference_silhouette.py` projects the per-object metrics into the compare payload |
| `server/adapters/mcp/contracts/vision.py`, `server/adapters/mcp/contracts/reference.py` | public capture + compare contracts | `VisionCaptureImageContract.view_kind` (`vision.py:22`) gains auxiliary kinds; `ReferenceSilhouetteAnalysisContract` / `ReferencePartSegmentationContract` (`reference.py:748-786`) receive deterministic per-object evidence |
| `server/adapters/mcp/vision/prompting.py`, `server/adapters/mcp/vision/config.py`, `server/adapters/mcp/vision/runner.py`, `server/infrastructure/config.py` | transport + budget | the flat IMAGES roster (`prompting.py:~497/511`), the image cap (`config.py:121` default 8, fail-safe `:28` = 12, `effective_max_images` `:133`), and the over-budget reject (`runner.py:170`) must stay honored when auxiliary captures are included |
| `tests/e2e/vision/`, `tests/e2e/integration/`, `tests/unit/adapters/mcp/`, `tests/fixtures/vision_eval/` | proof lanes | render-pass capture and per-object IoU are proven against repo fixtures, and contract parity is proven in `tests/unit/adapters/mcp/test_contract_payload_parity.py` |
| `_docs/_VISION/README.md`, `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`, `_docs/_ADDON/README.md`, `_docs/_MCP_SERVER/README.md`, `_docs/_TASKS/README.md` | canonical docs | docs must explain the deterministic auxiliary passes, per-object IoU, advisory posture, and budget behavior |

## Test Matrix

| Slice | Primary Validation Lane | Why |
|------|--------------------------|-----|
| addon object-ID / depth / normal pass + RPC parity | `tests/e2e/vision/test_reference_stage_silhouette_contract.py`, `tests/e2e/integration/test_guided_surface_contract_parity.py`, `tests/e2e/vision/test_reference_understanding_runtime_surface.py` | the pass producer is Blender behavior wired through RPC on both sides and must stay reversible and in parity |
| per-object mask IoU evidence | `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/fixtures/vision_eval/` golden fixtures | per-object IoU is deterministic and must be proven against repo-owned reference/capture fixtures |
| auxiliary-channel transmission + captions + budget | `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/e2e/vision/test_external_contract_profile_compare_path.py` | new `view_kind` values, captions, and budget-aware inclusion must not break the external payload or over-run the image cap |

## Acceptance Criteria

- a canonical target view can produce a deterministic object-ID mask image, a
  Z-depth image, and an optional normal image for the active camera, with the
  addon path main-thread-safe and reversible
  (`capture_scene_state` / `restore_scene_state`) and registered on **both** RPC
  sides
- `silhouette.py` can compute per-object mask IoU from the object-ID pass for
  each registered part present in the view, alongside (not replacing) the
  existing whole-frame `mask_iou`
- depth / normal / object-ID renders are transmitted to the VLM only as labeled
  auxiliary captures with explicit advisory captions, and including them never
  pushes the request past `effective_max_images` (`runner.py:170` still accepts)
- every depth/normal/object-ID-derived field keeps `not_truth_source` /
  `requires_deterministic_checks_for_correctness` framing; none of them can mark
  a gate complete or unlock a tool
- any magnitude surfaced is a proportional ratio against a trusted reference
  anchor, never an authoritative absolute measurement, and raw coordinates are
  never the primary evidence
- the optional monocular-depth hook for the reference image stays default-off and
  reuses the TASK-172 optional-runtime seam (no new provider-capability substrate)

> **Research caveat.** The cited benchmarks (SpatialRGPT depth connector,
> SD-VLM depth encoding, the spatial-reasoning survey, GPTEval3D / 3DGen-Bench
> normal-map passes) are indoor-scan / synthetic / text-to-3D evaluations, **not**
> Blender-vs-reference reconstruction. Treat the reported gains as directional
> motivation only; re-measure absolute gains on `tests/fixtures/vision_eval`
> golden fixtures before promoting any default behavior.

## Docs To Update

- `_docs/_TASKS/README.md`
- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_ADDON/README.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- split across the execution slices below; each child task owns its exact lane

## Changelog Impact

- completed implementation entries: changelogs 386, 387, 388, 389, 390, 391,
  and 393

## Status / Board Update

- `_docs/_TASKS/README.md` tracks `TASK-179` as a selected completed milestone
  on the Vision / Hybrid Loop lane
- child tasks remain nested historical slices and are all closed

## Validation Commands

- `git diff --check`
- `rg -n "TASK-179|Blender Depth, Normal And Object-ID Auxiliary Passes|Addon Object-ID, Depth And Normal Render Passes|Per-Object Mask IoU In Silhouette Evidence|Auxiliary-Channel Image Transmission And Captions" _docs/_TASKS/TASK-179*.md`

## Validation Category

- planning / governance / task-family definition
