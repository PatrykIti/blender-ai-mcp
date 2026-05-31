# TASK-180: Set-Of-Mark Object-Bound Visual Marks

**Status:** ✅ Done
**Progress:** Completed 2026-05-31. TASK-180-01 is complete: staged capture can emit default-off live `view_kind="overlay"` images with typed mark-id maps, packet mark legends, supplemental budget behavior, and Blender-backed proof. The 2026-05-31 closeout completes TASK-180-02, TASK-180-03, and TASK-180-04: mark IDs are registry/session-stable, optional reference-side marks reuse the default-off localization sidecar with provenance, and mark-keyed findings now produce typed correspondence plus one bounded validity retry.
**Priority:** 🔴 High
**Category:** Vision / Visual Prompting
**Estimated Effort:** Extra Large
**Follow-on After:** [TASK-179](./TASK-179_Blender_Depth_Normal_And_Object_ID_Auxiliary_Passes.md), [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md)
**Related:** [TASK-178](./TASK-178_Structured_Per_Finding_Compare_Schema.md), [TASK-181](./TASK-181_Scene_Graph_Diff_Compare_And_Registry_Scoped_Convergence.md), [TASK-173](./TASK-173_Reference_Guided_Creature_Scope_Convergence_And_Optional_Grounding_Followups.md)

## Relationship To Existing Board Items

- `TASK-179` is the upstream object-ID pass: it establishes which scene objects
  (registered parts) the compare path should treat as named, addressable parts.
  This family consumes that object-ID assignment and renders it as visible,
  numbered marks the VLM can key its findings to.
- `TASK-172` already shipped the optional, default-off vision capability runtime
  (localization and segmentation sidecars, lifecycle/TTL, packet-bounded
  activation). This family reuses that exact seam for the optional Grounded-SAM
  reference-marking path and must not reopen it or duplicate its transport.
- `TASK-178` (per-object compare evidence binding) and `TASK-181` (cross-view
  correspondence tables) are sibling consumers of the same object-ID substrate.
  This family supplies the visual-prompting layer (marks + mark-keyed findings)
  that those families parse and tabulate; the contracts must stay compatible.
- `TASK-173` proved the real failure mode where the creature loop cannot
  disambiguate similar appendages ("which of four legs?"). Object-bound marks
  are the direct remedy for that ambiguity at the perception layer.
- This umbrella is a standalone visual-prompting family. It does not reopen the
  generic provider-capability substrate owned by `TASK-140-06` / `TASK-172`.

## Objective

Give the VLM a visual handle on individual scene objects by overlaying
high-contrast numbered marks on each registered part, in both the render and
(optionally) the reference, with IDs that stay stable across views and across
iterate cycles. The compare path then requires findings keyed to those mark IDs,
parses them into a clean object-correspondence table mapped back to scene
objects, and rejects references to marks that do not exist.

After this family lands, a multi-part creature compare should no longer produce
prose like "one leg is too short" that the orchestrator cannot resolve; it
should produce mark-keyed evidence such as `mark 3 -> Leg_FrontLeft` with a
proportional ratio against a trusted anchor, so the orchestrating LLM can act on
the correct object.

## Business Problem

The verified compare path has no per-object binding:

- compare findings are bare `string[]` prose (`prompting.py` compare schema
  ~:1259-1300; `result_types.py` `VisionAssistContract.shape_mismatches` /
  `proportion_mismatches` are `list[str]`) with no `object_name` or
  `target_label` and no link back to a scene object.
- `assembled_target_scope` (a `SceneAssembledTargetScopeContract` with
  `object_names` and per-object `object_roles`) is carried on
  `VisionCaptureBundleContract.assembled_target_scope` (`contracts/vision.py:31`)
  but is never referenced in the parsed compare evidence, so the rich object/role
  structure the capture path already assembled is discarded at interpretation
  time.
- when several parts look alike (four legs, two ears, paired arms) the LLM
  cannot reliably tell which one a finding refers to; the prose names are
  ambiguous and the system deliberately projects away literal boxes to protect
  spatial reasoning, so there is no positional fallback either.
- the optional localization sidecars (`VisionLocalizationCandidate` with
  `box_xyxy`, `config.py:420`) default off and their candidates are never merged
  into the main compare schema, so even when enabled they do not give the LLM a
  stable per-object handle.
- `VisionCaptureImageContract.view_kind` already allows an `"overlay"` kind
  (`contracts/vision.py:22`), but no capture preset in `capture_runtime.py` ever
  produces an annotated overlay; the enum value is dead.

The result is that the orchestrator's hardest disambiguation task (mapping a
visible mismatch to the exact object to edit) is the one the perception layer
helps with least.

## Business Outcome

After this umbrella lands:

- the capture path can emit a deterministic `view_kind="overlay"` image with
  numbered, high-contrast marks anchored to each registered part from the staged
  object set, using deterministic isolate-per-object render footprints with no
  VLM and no SAM on the render side.
- the same part keeps the same mark number across every view (front/side/top/
  oblique) and across every iterate cycle, so the LLM and the orchestrator can
  refer to "mark 3" consistently within and between sessions steps.
- when the optional, default-off Grounded-SAM sidecar is enabled, the matching
  parts on the reference image carry the same ID scheme, making render-vs-
  reference correspondence explicit; when it is disabled the system degrades
  gracefully to render-only marks with no behavior regression.
- compare findings are required to be keyed to mark IDs and are parsed into an
  object-correspondence table mapped back to scene `object_name`s, so downstream
  edits target the correct object.
- a validity-retry guard rejects findings that cite non-existent marks, so the
  orchestrator never acts on a hallucinated part reference.

## Non-Goals

- do not make vision authoritative: mark-keyed findings remain VLM
  interpretation and must keep `not_truth_source=True` and
  `requires_deterministic_checks_for_correctness=True`. Deterministic
  inspection / assertion / silhouette continue to own scene truth. Marks and
  mark-keyed findings must not mark gates complete or unlock tools.
- do not emit any magnitude as an authoritative absolute measurement. Any
  size/length statement keyed to a mark must be a proportional ratio against a
  trusted reference anchor, never a metric absolute (VLMs are only ~37% within
  2x on metric tasks).
- do not turn on the Grounded-SAM (or any heavy) reference-marking sidecar by
  default. It stays default-off, advisory-only, packet-bounded, reusing the
  `TASK-172` optional-runtime seam. Do not reopen the `TASK-140-06`
  provider-capability substrate.
- do not emit raw coordinate / box tokens as the primary evidence carried to the
  orchestrator. Marks are symbolic IDs; the mark-keyed evidence is symbolic
  relations + proportional ratios, with coordinates available on demand only.
- do not add VLM-side chain-of-thought for spatial judgments about the marks;
  spatial reasoning stays in the orchestrator (VSI-Bench regresses -1..-21% with
  CoT for spatial tasks).
- do not introduce creature-only or squirrel-only mark logic; the mark scheme
  must work for any registered multi-part target.

## Execution Structure

| Order | Task | Purpose |
|------|------|---------|
| 1 | [TASK-180-01](./TASK-180-01_Object_ID_Driven_Numbered_Mark_Overlay_Render.md) | Object-ID-Driven Numbered Mark Overlay Render |
| 2 | [TASK-180-02](./TASK-180-02_Stable_Mark_Identifiers_Across_Views_And_Iterations.md) | Stable Mark Identifiers Across Views And Iterations |
| 3 | [TASK-180-03](./TASK-180-03_Reference_Image_Marks_Via_Optional_Grounded_SAM_Sidecar.md) | Reference-Image Marks Via Optional Grounded-SAM Sidecar |
| 4 | [TASK-180-04](./TASK-180-04_Mark_Keyed_Findings_Correspondence_Table_And_Validity_Retry.md) | Mark-Keyed Findings, Correspondence Table And Validity Retry |

## Repository Touchpoints

| Path / Module | Expected Ownership | Why It Is In Scope |
|---------------|--------------------|--------------------|
| `server/adapters/mcp/vision/capture_runtime.py` | deterministic capture-preset and bundle owner | the overlay preset (`view_kind="overlay"`) and the mark-render pass live here; the existing `CapturePresetSpec` only emits `wide`/`focus`, so the dead `overlay` enum value must finally be produced |
| `server/adapters/mcp/vision/silhouette.py` | deterministic mask / component analysis | per-part mask isolation and anchor placement (mark centroid per object) reuse the existing `_largest_component` / `_crop_bbox` machinery deterministically |
| `blender_addon/application/handlers/scene_viewport_mixin.py` | main-thread viewport capture | the addon side must support a per-object isolation/labelled-render pass so marks can be anchored on the correct projected object; both RPC sides stay in sync |
| `server/adapters/mcp/areas/reference_compare_packets.py`, `server/adapters/mcp/session_capabilities_registry.py` | packet planning and part-registry owner | mark IDs are assigned from the part registry so the same part keeps its number across views and iterate cycles; packets carry the mark-id map |
| `server/adapters/mcp/vision/reference_support.py`, `server/adapters/mcp/vision/config.py`, `server/adapters/mcp/vision/runtime.py` | optional sidecar config / activation | the optional, default-off Grounded-SAM reference-marking path reuses the `TASK-172` localization/segmentation seam (`runtime.py:230-252`, `VisionLocalizationConfig`/`VisionLocalizationCandidate` in `config.py`) |
| `server/adapters/mcp/vision/prompting.py`, `server/adapters/mcp/vision/parsing.py`, `server/adapters/mcp/sampling/result_types.py` | payload text, schema, parser, contracts | the IMAGES roster must carry mark context, the compare schema must allow mark-keyed findings, the parser must build the correspondence table and run the validity-retry guard, and the result contract must type the table |
| `server/adapters/mcp/contracts/vision.py` | capture image / bundle contracts | the overlay image and its mark-id map are typed here next to the existing `view_kind` literal and `assembled_target_scope` |
| `tests/unit/adapters/mcp/`, `tests/e2e/vision/`, `tests/fixtures/vision_eval/` | proof lanes | the overlay render, stable-ID behavior, optional sidecar degrade-to-render-only path, and mark-keyed parsing/validity-retry all need typed and golden-fixture proof |
| `_docs/_VISION/README.md`, `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md` | canonical vision docs | the visual-prompting layer, advisory posture, and optional Grounded-SAM activation must be documented |

## Test Matrix

| Slice | Primary Validation Lane | Why |
|------|--------------------------|-----|
| object-ID-driven overlay render | `tests/e2e/vision/test_reference_stage_silhouette_contract.py`, `tests/e2e/vision/` (new overlay-capture lane) | the overlay capture is a deterministic Blender-side artifact; it must be proven against a real isolated multi-part render |
| stable mark IDs across views/iterations | `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/e2e/vision/test_reference_guided_creature_comparison.py` | the same part must keep its number across front/side/top and across iterate cycles; packet-level assignment is deterministic and unit-testable |
| optional Grounded-SAM reference marks | `tests/unit/adapters/mcp/test_vision_runtime_config.py`, `tests/e2e/vision/` | the sidecar must stay default-off, advisory, packet-bounded, and degrade to render-only marks when disabled |
| mark-keyed findings + correspondence table + validity retry | `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/fixtures/vision_eval/` golden fixtures | mark-keyed parsing, mapping back to `object_name`, and rejection of non-existent marks must be deterministic and measured on golden fixtures |

## Acceptance Criteria

- the capture path can emit at least one `view_kind="overlay"` image whose marks
  are anchored to the registered parts from the `TASK-179` object-ID assignment,
  produced deterministically with no VLM and no SAM on the render side.
- marks are high-contrast numbered markers (red, ~10px target size per BLINK)
  legible at the capture resolution.
- the same registered part keeps the same mark number across all captured views
  in one bundle and across consecutive iterate cycles for one session target.
- when `VISION_LOCALIZATION_ENABLED` (Grounded-SAM reference-marking) is off, the
  system marks the render only and exhibits no regression vs the current
  no-overlay path; when on, the matching reference parts carry the same IDs.
- the compare result includes an object-correspondence table that maps each
  cited mark ID to a scene `object_name` (and role when known), and any
  magnitude attached to a mark is a proportional ratio versus a named anchor,
  never an absolute measurement.
- findings that cite a mark ID not present in the rendered mark set are rejected
  by a validity-retry guard, and the rejection is observable in the result
  envelope (the guard does not silently drop evidence without a note).
- `boundary_policy` on the vision result still reports `not_truth_source=True`
  and `requires_deterministic_checks_for_correctness=True`; marks never mark a
  gate complete or unlock a tool.
- RESEARCH CAVEAT: the cited benchmarks (Set-of-Mark, BLINK, GPT4Scene, etc.)
  are indoor-scan / synthetic, NOT Blender-vs-reference. Re-measure any absolute
  disambiguation or correspondence gain on `tests/fixtures/vision_eval` golden
  fixtures before promoting any default-on behavior.

## Docs To Update

- `_docs/_TASKS/README.md`
- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md` (optional Grounded-SAM env keys)
- `_docs/_TESTS/README.md`

## Tests To Add/Update

- split across the execution slices below; each child task owns its exact lane

## Changelog Impact

- completed through changelogs 378, 381, 392, and 393

## Status / Board Update

- `_docs/_TASKS/README.md` tracks `TASK-180` as a selected completed milestone
  on the Vision / Hybrid Loop lane
- child tasks remain nested historical slices and are all closed

## Validation Commands

- `git diff --check`
- `rg -n "TASK-180|Set-Of-Mark Object-Bound Visual Marks|Object-ID-Driven Numbered Mark Overlay Render|Stable Mark Identifiers|Reference-Image Marks Via Optional Grounded-SAM Sidecar|Mark-Keyed Findings" _docs/_TASKS/TASK-180*.md`

## Validation Category

- planning / governance / task-family definition
