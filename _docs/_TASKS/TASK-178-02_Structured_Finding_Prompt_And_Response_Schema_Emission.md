# TASK-178-02: Structured Finding Prompt And Response Schema Emission

**Parent:** [TASK-178](./TASK-178_Structured_Per_Finding_Compare_Schema.md)
**Status:** ✅ Done
**Completed:** 2026-05-30
**Priority:** 🔴 High
**Follow-on After:** [TASK-178-01](./TASK-178-01_Structured_Vision_Finding_Contract_Model.md)
**Objective:** Update the compare prompt text and `build_vision_response_json_schema` so the `generic_full` compare path requests structured per-finding objects (`finding`, `view_id`, `target_label`, `axis`, `direction`, `magnitude_ratio`, `reference_id`, `confidence`) instead of bare `string[]` arrays, with explicit instructions that `magnitude_ratio` is a proportional ratio against a named reference anchor and `target_label` uses the canonical role vocabulary. The `google_family_compare` profile keeps its narrower bare-string contract.

**Repository Touchpoints:** `server/adapters/mcp/vision/prompting.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/fixtures/vision_eval/`

**Acceptance Criteria:**
- the `generic_full` branch of `build_vision_response_json_schema` (`vision/prompting.py:1259-1300`) emits structured-object array items for the geometric-finding fields, with `axis` / `direction` as `enum`s, `magnitude_ratio` as `{"type": ["number", "null"]}`, and `confidence` as `{"type": "number", "minimum": 0.0, "maximum": 1.0}` inside each finding object
- the per-finding `target_label` schema description names the canonical role vocabulary as the expected value space
- the prompt text (`build_local_vision_payload_text` / `build_vision_payload_text`, around `vision/prompting.py:790-810`) instructs the model to return structured findings, to express magnitude only as a proportional ratio versus a reference anchor, and to never emit absolute measurements or raw coordinates
- the `_EXPECTED_KEYS` / `expected_json_keys(...)` surface (`vision/prompting.py:13-25`, `:825-848`) stays consistent with the new schema so parse-repair still recognizes the contract
- the `google_family_compare` branch (`vision/prompting.py:1245-1257`) and `_GEMINI_COMPARE_EXPECTED_KEYS` remain unchanged (bare strings), preserving the field-dropping profile behavior
- golden compare fixtures under `tests/fixtures/vision_eval/` are re-run and the structured-vs-flat output is captured for remeasurement before any promotion

## Implementation Notes

- the compare response schema is built in `build_vision_response_json_schema`
  (`server/adapters/mcp/vision/prompting.py:851`). The `generic_full` return at
  `:1259-1300` currently emits each geometric field as
  `{"type": "array", "items": {"type": "string"}}`. Change those array items to
  structured objects matching `VisionFinding` from TASK-178-01:
  - `finding`, `view_id`, `target_label` as strings (with `view_id` /
    `target_label` nullable)
  - `axis` and `direction` as `enum`s matching the `Literal` vocabularies
    introduced in TASK-178-01
  - `magnitude_ratio` as `{"type": ["number", "null"]}`
  - `reference_id` as `{"type": ["string", "null"]}`
  - `confidence` as `{"type": "number", "minimum": 0.0, "maximum": 1.0}` (mirror
    the `classification_scores` score bound at `vision/prompting.py:873`)
- keep `additionalProperties: False` and a `required` list on each finding
  object, consistent with the existing `likely_issues` / `recommended_checks`
  object schemas at `:1269-1295`.
- the prompt instructions that currently describe the flat fields live in
  `build_local_vision_payload_text` (`vision/prompting.py:790-810`):
  "Use shape_mismatches only for visible form/silhouette problems." etc. Update
  these to describe the structured finding shape, and add explicit guardrails:
  - "Express magnitude only as `magnitude_ratio`, a proportional ratio relative
    to the named `reference_id`; never report absolute sizes or units."
  - "Set `target_label` to a canonical role
    (`body_core`, `head_mass`, `tail_mass`, `snout_mass`, `ear_pair`,
    `eye_pair`, `foreleg_pair`, `hindleg_pair`) — these already appear at
    `vision/prompting.py:408`."
  - "Set `view_id` to the label of the view that revealed the finding."
  - "Do not emit raw pixel/world coordinates or bounding boxes."
- do **not** add VLM-side chain-of-thought instructions for the spatial
  judgment; keep the prompt to a single structured JSON answer (CoT for spatial
  reasoning regresses spatial benchmarks). The orchestrator does the reasoning.
- `build_vision_response_json_schema` is noted as never receiving
  `model_capabilities` (`vision/prompting.py:851`); this subtask must not change
  that or reopen the `TASK-140-06` capability substrate. The structured schema is
  selected purely by the existing `vision_contract_profile` / request routing.
- techniques to cite:
  - **GPTEval3D** (arXiv:2401.04092) — per-criterion judgments with a cited view
    motivate requiring `view_id` per finding
  - **SpatialRGPT** (arXiv:2406.01584) — six-quantity spatial schema motivates the
    `axis` / `direction` / `magnitude_ratio` decomposition in the requested JSON
  - **SpatialVLM** (arXiv:2401.12168) / **SD-VLM** (arXiv:2509.17664) —
    proportional reasoning supports the "ratio vs reference, never absolute"
    prompt guardrail
  - **SceneVerse** (arXiv:2401.09340) — relation triplets support the symbolic
    `target_label` + `reference_id` binding instead of coordinate tokens

## Pseudocode

```python
def _structured_finding_item_schema() -> dict[str, object]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "finding": {"type": "string"},
            "view_id": {"type": ["string", "null"]},
            "target_label": {
                "type": ["string", "null"],
                "description": (
                    "Canonical role: body_core, head_mass, tail_mass, snout_mass, "
                    "ear_pair, eye_pair, foreleg_pair, hindleg_pair."
                ),
            },
            "axis": {"type": ["string", "null"],
                     "enum": ["x", "y", "z", "width", "height", "depth", "none", None]},
            "direction": {"type": ["string", "null"],
                          "enum": ["too_large", "too_small", "too_wide", "too_narrow",
                                   "too_tall", "too_short", "shifted", "rotated",
                                   "none", None]},
            "magnitude_ratio": {"type": ["number", "null"],
                                "description": "Proportional ratio vs reference_id; never absolute."},
            "reference_id": {"type": ["string", "null"]},
            "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        },
        "required": ["finding", "view_id", "target_label", "axis",
                     "direction", "magnitude_ratio", "reference_id", "confidence"],
    }


# In the generic_full branch (prompting.py:1259-1300), replace the bare
# string arrays for shape/proportion findings with:
#   "shape_findings":      {"type": "array", "items": _structured_finding_item_schema()},
#   "proportion_findings": {"type": "array", "items": _structured_finding_item_schema()},
# while keeping the legacy keys available for the string projection path.
```

## Runtime / Security Contract Notes

- the requested schema and prompt stay strictly advisory. The model is asked for
  structured interpretation, not authoritative measurements; the
  `magnitude_ratio` guardrail ("proportional vs reference anchor, never
  absolute") must appear in both the schema description and the prompt text.
- no chain-of-thought is requested for the spatial judgment; reasoning stays in
  the orchestrator.
- no raw coordinate / bounding-box tokens are requested as primary evidence.
- this subtask changes prompt and schema emission only; it does not alter addon
  or Blender main-thread behavior, so no scene-state reversibility work is
  required. If a later golden-fixture re-run exercises live capture, that goes
  through the existing harness rather than new addon code.

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_compare_packets.py`
- `tests/fixtures/vision_eval/` (re-run golden compare fixtures such as
  `squirrel_head_to_body`, `squirrel_face_to_body`,
  `default_cube_to_picnic_table` and capture structured output for remeasurement)

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`

## Changelog Impact

- add/update a `_docs/_CHANGELOG/*` entry when this slice lands

## Status / Board Update

- board tracking remains on umbrella `TASK-178`
- no separate promoted board-row change is expected for this subtask unless it
  later becomes a standalone follow-on

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py` (when a golden-fixture re-run exercises live capture)

## Validation Category

- prompt / response-schema emission proof
