# TASK-178: Structured Per-Finding Compare Schema

**Status:** ✅ Done
**Completed:** 2026-05-30
**Completion Summary:** All subtasks shipped — TASK-178-01 (VisionFinding contract + `findings` field) and TASK-178-02 (strict-mode schema + parser coercion) via changelog 372, and TASK-178-03 (structured-findings propagation into the macro verification report) via changelog 379. Changelog 389 closes the audit drift by clamping top-level compare `confidence` to `[0, 1]` in the parser and range-validating the result contract.
**Priority:** 🔴 High
**Category:** Vision / Compare Output Contract
**Estimated Effort:** Large
**Follow-on After:** [TASK-171](./TASK-171_Creature_Attachment_First_Build_Contract_And_Structured_Vision_Handoff.md), [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md), [TASK-173](./TASK-173_Reference_Guided_Creature_Scope_Convergence_And_Optional_Grounding_Followups.md)
**Related:** [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md), [TASK-140](./TASK-140_Expand_External_Vision_Contract_Profiles_Across_Qwen_Anthropic_OpenAI_And_NVIDIA.md)

## Relationship To Existing Board Items

- This umbrella is a standalone follow-on family, not a child of the parents it
  references. `TASK-171`, `TASK-172`, and `TASK-173` are linked through
  **Follow-on After:** because they own upstream seams this work extends, not
  because this family lives under them.
- `TASK-171` already shipped the attachment-first creature handoff and the
  `target_label` canonical-role vocabulary used by reference understanding
  (`body_core`, `head_mass`, `tail_mass`, `snout_mass`, `ear_pair`, `eye_pair`,
  `foreleg_pair`, `hindleg_pair` — see `vision/prompting.py:408`). This family
  reuses that exact vocabulary for compare findings; it does not invent a new
  role taxonomy.
- `TASK-172` shipped the optional-runtime seam, including
  `VisionLocalizationCandidate` (`vision/config.py:420`) which already carries
  `box_xyxy`, `target_view`, and a range-validated `confidence`. That proves the
  data model can already carry per-finding view/binding/confidence. This family
  merges that shape into the **main compare schema**, which is still a flat
  `list[str]`. It must not reopen the `TASK-140-06` provider-capability
  substrate.
- `TASK-173` is the creature scope-convergence consumer follow-on. Its planner
  and gate decisions are currently fed flat string findings with no object/axis
  binding; this family is what lets that planner consume object + axis + ratio.
- `TASK-166` owns the hierarchical packet compare and evidence taxonomy this
  schema flows through; `TASK-140` owns the per-provider contract profiles
  (`generic_full`, `google_family_compare`) that this schema must keep coherent.

## Objective

Replace the bare `list[str]` geometric-finding fields in the compare schema with
a list of typed structured findings, so that each finding can state which view
revealed it, which scene object/part role it concerns, which axis and direction,
and by how much (as a proportional ratio against a trusted reference anchor).
After this family lands, the orchestrating LLM and the repair planner receive
findings such as "head_mass too wide on X axis, ~1.4x vs body_core, seen in
front_view" instead of an unbound "head too wide" string, while the output stays
strictly advisory and backward-compatible for weaker models.

## Business Problem

The compare schema in `vision/prompting.py:1259-1300` makes every geometric
finding a bare string array: `visible_changes`, `shape_mismatches`,
`proportion_mismatches`, `correction_focus`, and `next_corrections` are all
`{"type": "array", "items": {"type": "string"}}`, and `captures_used` is a
single flat `list[str]`. The matching contract `VisionAssistContract`
(`sampling/result_types.py:159-168`) mirrors that with `list[str]` fields. As a
direct result:

- a finding like "head too wide" cannot say **which view** revealed it, so the
  orchestrator cannot tell whether it is a real proportion problem or a single
  bad camera angle
- it cannot say **which scene object/part role** it concerns, so the planner in
  `areas/reference_planner.py` (`_local_form_reason` at `:408`, the proportion
  blockers at `:368`) has to re-derive the target by string matching
- it cannot say **which axis** or **direction**, so "too wide" and "too tall"
  collapse into the same opaque text
- it cannot say **by how much**, so there is no proportional signal to rank one
  mismatch above another
- `VisionLocalizationCandidate` (`vision/config.py:420`) already proves the data
  model can carry `box_xyxy` / `target_view` / range-validated `confidence`, but
  it is never merged into the main compare schema
- compare `confidence` is not range-validated: `parsing.py:1365-1367` only
  checks `isinstance(confidence, (int, float))` and otherwise nulls it, so a
  model returning `confidence: 7` or `confidence: -0.3` is passed through
  unclamped

This is not a runtime-availability gap. The VLM transmit paths
(`vision/backends.py:849-916`) and the parser (`vision/parsing.py:1315-1428`)
already work; the **output contract** is simply too coarse to support
object-aware, axis-aware, magnitude-aware spatial reasoning in the orchestrator.

## Business Outcome

After this umbrella lands:

- each compare finding is a typed object carrying `finding`, `view_id`,
  `target_label` (canonical role), `axis`, `direction`, `magnitude_ratio`,
  `reference_id`, and `confidence`
- `magnitude_ratio` is always a **proportional ratio** against a named reference
  anchor (`reference_id`), never an absolute measurement
- weak/legacy models still work: structured findings degrade to the existing
  flat string projection so nothing downstream breaks before the structured
  path is wired through
- the parser clamps `confidence` to `[0, 1]`, normalizes `axis` / `direction`
  to a fixed vocabulary, and defaults missing fields safely
- the repair planner and macro reporting can route on `target_label` + `axis` +
  `magnitude_ratio` instead of re-deriving them from free text
- vision output remains advisory; the richer fields do not give vision any new
  authority over gates, tool unlocks, or scene truth

## Non-Goals

- do not let vision become a truth source: structured findings are still VLM
  interpretation and must keep `not_truth_source` /
  `requires_deterministic_checks_for_correctness`. Deterministic inspection,
  assertion, and silhouette metrics own scene truth. Vision must not mark gates
  complete or unlock tools.
- do not treat `magnitude_ratio` as an authoritative absolute measurement. It is
  a **proportional ratio versus a trusted reference anchor only** (VLMs land
  within 2x of true metric magnitudes only ~37% of the time on metric tasks);
  never emit it as an absolute size.
- do not turn on or require any heavier perception sidecar
  (SAM / SAM2 / GroundingDINO / Depth-Anything / CLIP / DINO embeddings). Those
  stay default-off, advisory-only, and packet-bounded per the `TASK-172`
  optional-runtime seam, and this family must not reopen the `TASK-140-06`
  provider-capability substrate.
- do not emit raw coordinate tokens as primary evidence. Prefer symbolic
  relations plus proportional ratios; coordinates / boxes stay on-demand only
  (raw coordinates measurably hurt LLM spatial reasoning).
- do not add VLM-side chain-of-thought for spatial judgments; reasoning stays in
  the orchestrator (CoT for spatial judgments regresses spatial benchmarks).
- do not invent a new role taxonomy; reuse the existing reference-understanding
  canonical-role vocabulary for `target_label`.

## Execution Structure

| Order | Task | Purpose |
|------|------|---------|
| 1 | [TASK-178-01](./TASK-178-01_Structured_Vision_Finding_Contract_Model.md) | Structured Vision Finding Contract Model |
| 2 | [TASK-178-02](./TASK-178-02_Structured_Finding_Prompt_And_Response_Schema_Emission.md) | Structured Finding Prompt And Response Schema Emission |
| 3 | [TASK-178-03](./TASK-178-03_Finding_Parser_Coercion_And_Planner_Reporting_Propagation.md) | Finding Parser Coercion And Planner/Reporting Propagation |

## Repository Touchpoints

| Path / Module | Expected Ownership | Why It Is In Scope |
|---------------|--------------------|--------------------|
| `server/adapters/mcp/sampling/result_types.py` | `VisionAssistContract` and the new `VisionFinding` contract | the flat `list[str]` fields at `:159-168` are the public compare model that must gain typed findings while keeping string projections |
| `server/adapters/mcp/contracts/reference.py` | canonical role vocabulary and `ReferenceCorrectionVisionEvidenceContract` (`:466`) | `target_label` reuses the existing reference-understanding role labels; the planner's vision-evidence contract must carry object/axis/ratio downstream |
| `server/adapters/mcp/vision/prompting.py` | compare prompt text and `build_vision_response_json_schema` (`:851`) | the bare string-array schema at `:1259-1300` and the matching prompt instructions at `:790-810` must request structured findings |
| `server/adapters/mcp/vision/parsing.py` | `_normalize_payload` (`:1315`) and confidence handling (`:1365`) | the parser must coerce/clamp structured findings, validate `confidence` to `[0, 1]`, and normalize axis/direction safely |
| `server/adapters/mcp/vision/reporting.py` | `_vision_recommendations_for_macro` (`:30`) | macro follow-up recommendations should carry object + axis + ratio instead of generic "vision flagged mismatches" text |
| `server/adapters/mcp/areas/reference_planner.py` | `_local_form_reason` (`:408`), `_proportion_planner_blockers` (`:368`) | the planner should route on structured `target_label` + `axis` + `magnitude_ratio` rather than re-deriving them from free strings |
| `tests/unit/adapters/mcp/`, `tests/fixtures/vision_eval/` | proof lanes and golden fixtures | contract parity, packet, and reference-image lanes plus the golden compare fixtures must prove structured findings and string-projection fallback |

## Test Matrix

| Slice | Primary Validation Lane | Why |
|------|--------------------------|-----|
| structured finding contract + backward-compatible projection | `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py` | the public contract must round-trip structured findings and still expose flat string projections for weak models |
| prompt + response schema emission | `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/fixtures/vision_eval/` | the requested schema and prompt must ask for structured findings with proportional ratios and canonical labels, and golden fixtures must remeasure quality |
| parser coercion + planner/reporting propagation | `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py` | confidence clamping, axis/direction normalization, and object/axis/ratio propagation into reporting and the planner must be deterministic |

## Acceptance Criteria

- the main compare schema (`vision/prompting.py:1259-1300`) requests structured
  per-finding objects, not bare `string[]`, for the geometric-finding fields
- each emitted finding carries `finding`, `view_id`, `target_label`, `axis`,
  `direction`, `magnitude_ratio` (`float | null`), `reference_id`, and
  `confidence`
- `target_label` is drawn from the existing reference-understanding canonical
  role vocabulary, not a new taxonomy
- `magnitude_ratio` is always a proportional ratio relative to `reference_id`
  and is documented as never an absolute measurement
- weak/legacy or `google_family_compare` models that return flat strings still
  parse cleanly into the same `VisionAssistContract` via a string projection
- the parser clamps compare `confidence` (and per-finding `confidence`) to
  `[0, 1]`, normalizes `axis` / `direction`, and defaults missing fields safely
- `areas/reference_planner.py` and `vision/reporting.py` can route on
  `target_label` + `axis` + `magnitude_ratio` from a structured finding
- the `boundary_policy` posture is unchanged: findings stay advisory,
  `not_truth_source`, and cannot mark gates complete or unlock tools
- benchmark caveat is documented (below) and golden-fixture gains are remeasured
  before any promotion

> Research caveat: the cited benchmarks (SpatialRGPT, SceneVerse, ShapeLLM,
> GPTEval3D, SpatialVLM / SD-VLM) are indoor-scan / synthetic, **not**
> Blender-vs-reference. Any absolute quality gain from structured findings must
> be re-measured on the `tests/fixtures/vision_eval/` golden fixtures (e.g.
> `squirrel_head_to_body`, `default_cube_to_picnic_table`) before promotion.

## Docs To Update

- `_docs/_TASKS/README.md`
- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- split across the execution slices below; each child task owns its exact lane

## Changelog Impact

- planning-only now; add a `_docs/_CHANGELOG/*` entry when the first slice lands
- do not treat this planning-only task creation as the changelog event

## Status / Board Update

- `_docs/_TASKS/README.md` should track `TASK-178` as an open item on the
  Vision / Hybrid Loop lane
- child tasks stay nested under the open umbrella and do not need board rows
  unless one later becomes a separately promoted follow-on
- the coordinator owns the board update; this task family does not edit
  `_docs/_TASKS/README.md`

## Validation Commands

- `git diff --check`
- `rg -n "TASK-178|Structured Per-Finding Compare Schema|Structured Vision Finding Contract Model|Structured Finding Prompt And Response Schema Emission|Finding Parser Coercion" _docs/_TASKS/TASK-178*.md`

## Validation Category

- planning / governance / task-family definition
