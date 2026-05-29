# TASK-174-02: Caption Helper, Payload Parity Tests And Docs

**Parent:** [TASK-174](./TASK-174_Per_Image_Caption_Interleaving_For_Vision_Payloads.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Follow-on After:** [TASK-174-01](./TASK-174-01_Caption_Interleaving_In_Both_Transmit_Paths.md)
**Objective:** Extract a single caption-formatting helper reused by both transmit paths and the flat roster, add payload-parity unit coverage proving every image blob is immediately preceded by its caption in both providers, and document the per-image grounding convention so future capture/roster changes keep one format.

**Repository Touchpoints:** `server/adapters/mcp/vision/prompting.py` (shared caption helper; `IMAGES`/`REFERENCE_IMAGES` roster lines ~`:497`, `:539`, `:586`, `:629`, `:770`), `tests/unit/adapters/mcp/test_vision_external_backend.py` (provider request-payload capture lanes; home of the caption-then-blob parity walk), `tests/unit/adapters/mcp/test_vision_prompting.py` (roster/caption format lane), `_docs/_VISION/README.md`, `_docs/_VISION/MULTI_VIEW_CAPTURE_PLAN.md`

**Acceptance Criteria:**
- A single caption-formatting helper in `server/adapters/mcp/vision/prompting.py` is the only source of the per-image caption format and is consumed by both the `google_ai_studio` and OpenAI/OpenRouter interleaving (from `TASK-174-01`) and by the flat `IMAGES`/`REFERENCE_IMAGES` roster lines.
- A payload-parity test proves, for a representative multi-image request, that in both providers each image blob is immediately preceded by exactly one caption text part for that image (caption-then-blob alternation), with one leading payload-text part first.
- The helper is deterministic and symbolic: same `VisionImageInput` yields the same caption; the caption contains label, role, and derivable view/stage only, with no raw coordinate tokens, no absolute metric magnitudes, and no chain-of-thought.
- `_docs/_VISION/README.md` and `_docs/_VISION/MULTI_VIEW_CAPTURE_PLAN.md` describe the grounding convention (caption-then-blob in both providers; roster kept as a redundant index).
- No public contract changes; full `tests/unit` and the vision e2e lanes still pass.

## Implementation Notes

- The flat roster lines today are duplicated string-builds of
  `f"- {image.role}: {image.label or image.role}"` across
  `_build_gemini_compare_payload_text` (`:497`),
  `_build_reference_understanding_payload_text` (`:539`), the reference-classification
  builder (`:586`), `build_vision_payload_text` packet branch (`:629`), and the
  local payload-text builder `build_local_vision_payload_text` (`:770`).
  Extracting one helper (for example
  `format_image_caption(image: VisionImageInput) -> str` plus a thin
  `format_image_roster_line(image)` wrapper) removes that duplication and lets the
  interleaved captions from `TASK-174-01` and the roster share one format.
- The caption is derived from data already on `VisionImageInput`
  (`server/adapters/mcp/vision/backend.py:17-24`): `role`
  (`before`/`after`/`reference`) and `label`. The view/stage tokens come from
  parsing the label the capture layer already produces (capture labels are built
  upstream from `VisionCaptureImageContract.view_kind` / `preset_name` and the
  before/after stage, e.g. a label like `target_front_after`). The helper must
  degrade gracefully: when a view or stage token cannot be derived, omit that
  token rather than emitting a placeholder.
- Parity testing approach: the external backend tests already capture the
  outgoing payload as a dict (`captured["json"]`). A parity test can walk
  `contents[0]["parts"]` (Gemini) and `messages[1]["content"]` (OpenAI/OpenRouter)
  and assert that the parts after the leading text element strictly alternate
  caption-text then image-part, and that each caption references the matching
  image label. The provider-specific parity assertions live in
  `tests/unit/adapters/mcp/test_vision_external_backend.py` (which already
  captures the outgoing request payload); `test_contract_payload_parity.py`
  stays scoped to Pydantic `MCPContract` construction and is not used for the
  request-payload-shape walk.
- Relevant techniques to cite as design basis (advisory only; re-measure on
  Blender fixtures before claiming gains):
  - Set-of-Mark Prompting (arXiv:2310.11441) — per-image marks improve
    attribution; the helper is the single mark format.
  - ViP-LLaVA (arXiv:2312.00784) — adjacent textual references bind the model to
    the intended image.
  - VLM-Grounder (arXiv:2410.13860) — image-level identity cues alongside each
    image aid zero-shot 3D grounding.

## Pseudocode

```python
def format_image_caption(image: VisionImageInput) -> str:
    label = image.label or image.role
    tokens = [f"image: {label}", f"role={image.role}"]
    view = _derive_view_token(label)    # e.g. "front" from "target_front_after"; None if absent
    stage = _derive_stage_token(label)  # e.g. "after"; None if absent
    if view:
        tokens.append(f"view={view}")
    if stage:
        tokens.append(f"stage={stage}")
    return "[" + " | ".join(tokens) + "]"


def format_image_roster_line(image: VisionImageInput) -> str:
    # roster stays a redundant index, using the same caption source of truth
    return f"- {format_image_caption(image)}"
```

```python
# Parity assertion sketch (provider-agnostic walk)
def assert_caption_then_blob(parts, *, blob_key):
    body = parts[1:]  # skip the single leading payload-text part
    assert len(body) % 2 == 0
    for caption_part, blob_part in zip(body[0::2], body[1::2]):
        assert _is_text_part(caption_part)
        assert blob_key in blob_part  # "inline_data" for Gemini, "image_url" for OpenAI/OpenRouter
```

## Runtime / Security Contract Notes

- The helper only formats advisory grounding text. It does not change what vision
  is allowed to assert: findings remain `not_truth_source` /
  `requires_deterministic_checks_for_correctness`, and deterministic inspection /
  assertion / silhouette still own scene truth. Captions never mark gates
  complete or unlock tools.
- Caption content stays symbolic (label/role/view/stage). No raw coordinate
  tokens, no absolute metric magnitudes (size language stays a proportional ratio
  vs a trusted reference anchor elsewhere), and no chain-of-thought.
- Heavier perception sidecars (SAM/SAM2/GroundingDINO/Depth-Anything/CLIP/DINO)
  stay DEFAULT-OFF and out of scope; the helper does not depend on them.
- No Blender / addon behavior changes, so no `capture_scene_state` /
  `restore_scene_state` interaction is required for this slice.

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_prompting.py` — assert the shared helper
  is deterministic and symbolic, and that the roster line uses the helper output.
- `tests/unit/adapters/mcp/test_vision_external_backend.py` — add the
  caption-then-blob parity check covering both providers for a representative
  multi-image request (walking the captured request payload), and keep/extend the
  provider-specific caption-interleaving assertions added in `TASK-174-01` so the
  shared helper does not regress either branch.

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_VISION/MULTI_VIEW_CAPTURE_PLAN.md`

## Changelog Impact

- add/update a `_docs/_CHANGELOG/*` entry when this slice lands

## Status / Board Update

- board tracking remains on umbrella `TASK-174`
- no separate promoted board-row change is expected for this subtask unless it
  later becomes a standalone follow-on

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_vision_external_backend.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py` (run when external transmit behavior is exercised against a live provider lane)

## Validation Category

- vision payload-grounding parity and documentation proof
