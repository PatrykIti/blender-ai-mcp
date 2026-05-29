# TASK-176: Capture-Failure And Evidence-Truncation Signal Surfacing

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Vision / Reliability And Observability
**Estimated Effort:** Medium
**Follow-on After:** [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md), [TASK-173](./TASK-173_Reference_Guided_Creature_Scope_Convergence_And_Optional_Grounding_Followups.md)
**Related:** [TASK-167](./TASK-167_Cross_Module_Debug_Profile_Registry_And_Runtime_Logging.md), [TASK-169](./TASK-169_Reference_Guided_Quality_Drift_Regression_And_Runtime_Authority.md)

## Relationship To Existing Board Items

- `TASK-172` shipped the optional vision-capability runtime and the
  default-off, advisory-only, packet-bounded sidecar seam. This family does not
  reopen that substrate; it hardens the deterministic capture and parse path
  that feeds every vision invocation regardless of whether any optional sidecar
  is active.
- `TASK-173` repaired creature-scope convergence and packet arbitration, but it
  assumed that the captures reaching the VLM are the views they claim to be and
  that an empty evidence list means "nothing to correct". This family supplies
  the missing trust signals so that assumption is no longer silent.
- `TASK-167` established cross-module debug-profile instrumentation; the new
  capture-failure and truncation markers should be surfaceable through the same
  reference/vision debug profile rather than a parallel logging path.
- `TASK-169` owns the reference-guided quality-drift regression lanes and the
  runtime-authority posture; this family adds the observability signals those
  regression lanes can assert on without changing gate authority.
- This umbrella is a standalone reliability/observability follow-on. It links
  its upstream parents through **Follow-on After** and **Related** only; its own
  subtasks use **Parent** pointing back at this umbrella.

## Objective

Make capture failures and evidence truncation observable, deterministic, and
additive so the orchestrating LLM can tell trustworthy visual evidence apart
from silently degraded evidence. Today a headless Blender camera operation can
return an error string instead of raising, the capture runtime swallows it with
`except Exception: pass`, and a `target_top` capture that is actually a front
view still reaches the VLM labeled `target_top` with full confidence. In
parallel, finding lists are hard-sliced with no omitted-count marker and repair
payloads can emit empty-but-valid contracts that read like "the scene looks
correct". After this family lands, a mislabeled or failed view carries
`capture_ok=False` / `capture_warning`, truncated lists carry
`evidence_truncated` + `omitted_count`, and an unusable analysis carries an
explicit `analysis_unusable` flag distinct from `confidence == 0.0`.

## Business Problem

The deterministic capture and parse path that feeds the VLM currently hides its
own failures, which is the verified root of the "squirrel mislabeled-view"
failure class:

- `capture_stage_images` in
  `server/adapters/mcp/vision/capture_runtime.py` wraps every camera operation
  in `except Exception: pass` (lines 211, 216, 221, 232). It calls
  `scene_handler.isolate_object(...)`, `scene_handler.set_standard_view(...)`,
  `scene_handler.camera_focus(...)`, and `scene_handler.camera_orbit(...)`.
- In headless or background Blender, those handlers do not raise on the common
  "no active 3D viewport" condition; they RETURN an error string. The addon
  proves this directly: `set_standard_view` returns
  `"No 3D viewport found. Standard view requires an active 3D view."`
  (`blender_addon/application/handlers/scene_viewport_mixin.py:1100`),
  `camera_focus` returns
  `"No 3D viewport found. Camera focus requires an active 3D view."` (line 364),
  and `camera_orbit` returns
  `"No 3D viewport found. Camera orbit requires an active 3D view."` (line 323).
- `capture_stage_images` discards those return values entirely, then still
  appends a `VisionCaptureImageContract` whose `label` is `f"{preset.name}_{stage}"`
  (line 251) and whose `preset_name` claims the intended view. A `target_top`
  preset that never actually changed the view therefore reaches the VLM as a
  fully-trusted top capture, and the VLM compares a front-looking image against
  a top reference with no way to know the view label is wrong.
- Evidence lists are hard-capped without any omitted-count marker.
  `_bounded_string_list` defaults to `max_items=3`
  (`server/adapters/mcp/vision/parsing.py:318/322`) and slices `visible_changes`,
  `shape_mismatches`, `proportion_mismatches`, `correction_focus`, and
  `next_corrections` in `_normalize_payload` (parsing.py:1326-1363).
  `synthesize_packet_vision_result` slices the merged evidence to `[:8]` and
  `[:6]` (`server/adapters/mcp/areas/reference_compare_packets.py:1273-1285`,
  `1358`, `1360`). None of these emit how many findings were dropped, so the
  orchestrator cannot tell a complete result from a truncated one.
- Repair payloads emit empty-but-valid contracts that look clean. `_repair_echo_payload`,
  `_repair_label_map_payload`, and `_repair_unrecognized_payload`
  (parsing.py:205-272) all return empty `visible_changes` / `shape_mismatches` /
  `proportion_mismatches` lists with `confidence: 0.0`. Downstream, `confidence ==
  0.0` is indistinguishable from "the model is genuinely unsure but the scene is
  fine", so a failed parse can read like a clean comparison.

This is not a "vision model is wrong" problem and not an "optional sidecar is
down" problem. It is a missing-signal problem in the deterministic plumbing: the
capture runtime and parser already know when something went wrong, and they
throw that knowledge away before it reaches the orchestrator.

## Business Outcome

After this umbrella lands:

- a capture image that came from a camera operation which returned an error
  string carries `capture_ok=False` and a bounded `capture_warning`, and the
  bundle carries a `capture_warnings` list summarizing per-image failures, so a
  mislabeled or failed view can be down-weighted or skipped instead of trusted
- the orchestrating LLM can distinguish "this top view is reliable" from "this
  top view may actually be a different orientation" before it acts on visual
  comparison evidence
- every finding list that is hard-sliced carries `evidence_truncated` and
  `omitted_count`, so "no further mismatches" is no longer ambiguous with "more
  mismatches existed but were dropped to stay within bounds"
- repair and compare payloads carry a top-level `analysis_unusable` flag that is
  explicitly distinct from `confidence == 0.0`, so the orchestrator can tell
  "empty because the comparison was actually clean" from "empty because the
  analysis failed and must not be read as a clean result"
- all of these signals are additive, deterministic, and non-authoritative: they
  describe the reliability of the evidence, they do not assert scene truth and
  they do not unlock or complete any gate

## Non-Goals

- Vision stays **advisory**. The new fields (`capture_ok`, `capture_warning`,
  `capture_warnings`, `evidence_truncated`, `omitted_count`,
  `analysis_unusable`) are still VLM-side or capture-side interpretation and
  must keep the existing boundary posture: `not_truth_source`,
  `requires_deterministic_checks_for_correctness`. Deterministic inspection,
  assertion, and silhouette checks continue to own scene truth. None of these
  new fields may mark a gate complete or unlock a tool.
- Do not turn `capture_ok=False` into a hard failure that aborts the bundle by
  default; it is a reliability annotation the orchestrator and policy can act
  on, not a new authority over the loop.
- Do not emit magnitudes as authoritative absolute measurements. Any sizing or
  drift hints remain **proportional ratios vs a trusted reference anchor**; a
  VLM is only ~37% within 2x on metric tasks, so absolute pixel/world numbers
  must never be treated as truth.
- Do not reopen the heavier optional perception sidecars (SAM / SAM2 /
  GroundingDINO / Depth-Anything / CLIP / DINO embeddings). They stay
  default-off, advisory-only, and packet-bounded per the `TASK-172`
  optional-runtime seam, and this family must not reopen the `TASK-140-06`
  provider-capability substrate.
- Do not emit raw coordinate tokens as primary evidence. Capture-failure and
  truncation signals are symbolic flags and counts; coordinates stay on-demand
  only, since raw coordinate tokens degrade LLM spatial reasoning (3DGraphLLM
  50.1 -> 42.6; Text-Scene relations 59.4 vs coordinates 18.4).
- Do not add VLM-side chain-of-thought for spatial judgments. Reasoning about
  what to do with a degraded capture or a truncated list stays in the
  orchestrator; injected CoT regresses spatial perception (VSI-Bench -1..-21%).

## Execution Structure

| Order | Task | Purpose |
|------|------|---------|
| 1 | [TASK-176-01](./TASK-176-01_Capture_Ok_And_Warning_Signals_For_Capture_Bundles.md) | Capture-Ok And Warning Signals For Capture Bundles |
| 2 | [TASK-176-02](./TASK-176-02_Evidence_Truncation_And_Analysis_Unusable_Markers.md) | Evidence-Truncation And Analysis-Unusable Markers |

## Repository Touchpoints

| Path / Module | Expected Ownership | Why It Is In Scope |
|---------------|--------------------|--------------------|
| `server/adapters/mcp/vision/capture_runtime.py` | capture orchestration owner | `capture_stage_images` swallows camera-op return strings at lines 211/216/221/232 and still appends fully-trusted contracts; it must record per-image and bundle-level capture reliability |
| `server/adapters/mcp/contracts/vision.py` | capture-image and capture-bundle contract owner | `VisionCaptureImageContract` and `VisionCaptureBundleContract` need the additive `capture_ok` / `capture_warning` / `capture_warnings` fields |
| `blender_addon/application/handlers/scene_viewport_mixin.py` | addon camera/view handler owner | `set_standard_view` / `camera_focus` / `camera_orbit` already return error strings instead of raising; this family reads those returns rather than discarding them, and keeps both RPC sides aligned |
| `server/adapters/mcp/vision/parsing.py` | vision response normalization owner | `_normalize_payload` and `_bounded_string_list` hard-slice findings with no omitted-count; repair payloads (205-272) emit empty-but-valid contracts that need `analysis_unusable` |
| `server/adapters/mcp/sampling/result_types.py` | public vision result contract owner | `VisionAssistContract` needs the additive `evidence_truncated`, `omitted_count`, and `analysis_unusable` fields while keeping `VisionBoundaryPolicyContract` intact |
| `server/adapters/mcp/areas/reference_compare_packets.py` | packet synthesis owner | `synthesize_packet_vision_result` hard-slices merged findings to `[:8]`/`[:6]` and already carries `budget_notes`; the new truncation markers extend that precedent |
| `tests/unit/adapters/mcp/`, `tests/e2e/vision/`, `tests/e2e/integration/` | proof-lane owners | the failure class came from a real headless capture path, so the fix must prove failure-string detection, truncation marking, and unusable-analysis distinction with repo-owned lanes |
| `_docs/_VISION/*`, `_docs/_TASKS/README.md` | canonical docs and board | docs must explain the new reliability signals and the advisory boundary they preserve |

## Test Matrix

| Slice | Primary Validation Lane | Why |
|------|--------------------------|-----|
| capture-ok and capture-warning surfacing | `tests/unit/adapters/mcp/test_vision_capture_runtime.py`, `tests/unit/adapters/mcp/test_vision_capture_bundle.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/e2e/vision/test_reference_understanding_runtime_surface.py` | the capture-runtime test already mocks `set_standard_view` / `camera_focus` / `camera_orbit` return strings, so a failure-string mock can prove the new flags |
| evidence truncation markers | `tests/unit/adapters/mcp/test_vision_parsing.py`, `tests/unit/adapters/mcp/test_vision_result_types.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py` | `_normalize_payload` and `synthesize_packet_vision_result` are the exact slicing sites and already have dedicated unit lanes |
| analysis-unusable distinction | `tests/unit/adapters/mcp/test_vision_parsing.py`, `tests/unit/adapters/mcp/test_vision_result_types.py`, `tests/e2e/vision/test_external_contract_profile_compare_path.py` | repair payloads (205-272) need `analysis_unusable=True` distinct from `confidence == 0.0`, and the external compare path proves it end to end |

## Acceptance Criteria

- a capture image produced by a camera operation that returned a non-`None`
  error string carries `capture_ok=False` and a bounded `capture_warning`, while
  a successful capture carries `capture_ok=True` and no warning
- the assembled capture bundle exposes a `capture_warnings` list that summarizes
  every per-image capture failure for the stage, so the orchestrator sees the
  failure without inspecting each image contract
- a `target_top` (or any standard-view / focus / orbit) preset whose view
  operation failed never reaches the VLM as a fully-trusted view; the
  reliability annotation travels with that image
- every finding list that is hard-sliced (`_normalize_payload` and
  `synthesize_packet_vision_result`) emits `evidence_truncated=True` and an
  `omitted_count` equal to the number of deduped findings dropped, and emits
  `evidence_truncated=False` with `omitted_count=0` when nothing was dropped
- repair payloads (`_repair_echo_payload`, `_repair_label_map_payload`,
  `_repair_unrecognized_payload`) carry `analysis_unusable=True`, while a
  genuinely clean comparison carries `analysis_unusable=False` even when
  `confidence` is low or `0.0`
- every new field is additive and optional in the contract, defaults to a
  reliability-neutral value, and keeps `VisionBoundaryPolicyContract` asserting
  `not_truth_source` / `requires_deterministic_checks_for_correctness`; no new
  field marks a gate complete or unlocks a tool
- **Research caveat:** the cited benchmarks (DiffuRank, 3DSRBench, LL3M) are
  indoor-scan / synthetic / agentic-mesh studies, not Blender-vs-reference
  measurements. Re-measure any claimed reliability or convergence gain on the
  `tests/fixtures/vision_eval` golden fixtures before promoting this family from
  planning to a shipped, measured improvement.

## Docs To Update

- `_docs/_TASKS/README.md`
- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TESTS/README.md`

## Tests To Add/Update

- split across the execution slices below; each child task owns its exact lane

## Changelog Impact

- planning-only now; add a `_docs/_CHANGELOG/*` entry when the first slice lands
- do not treat this planning-only task creation as the changelog event

## Status / Board Update

- `_docs/_TASKS/README.md` should track `TASK-176` as a promoted open item on the
  Vision / Hybrid Loop lane
- child tasks stay nested under the open umbrella and do not need board rows
  unless one later becomes a separately promoted follow-on
- the coordinator owns the board update; this family does not edit
  `_docs/_TASKS/README.md` directly

## Validation Commands

- `git diff --check`
- `rg -n "TASK-176|Capture-Failure And Evidence-Truncation Signal Surfacing|Capture-Ok And Warning Signals|Evidence-Truncation And Analysis-Unusable Markers|capture_ok|capture_warning|evidence_truncated|omitted_count|analysis_unusable" _docs/_TASKS/TASK-176*.md`

## Validation Category

- planning / governance / task-family definition
