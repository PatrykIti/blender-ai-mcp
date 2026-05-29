# TASK-174-01: Caption Interleaving In Both Transmit Paths

**Parent:** [TASK-174](./TASK-174_Per_Image_Caption_Interleaving_For_Vision_Payloads.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Follow-on After:** [TASK-171](./TASK-171_Creature_Attachment_First_Build_Contract_And_Structured_Vision_Handoff.md), [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md)
**Objective:** Interleave a deterministic one-line caption text part immediately before each image part in both the `google_ai_studio` (inline_data) and the OpenAI/OpenRouter (image_url) payload branches of the external backend, so the orchestrating VLM binds each blob to its correct label/role/view/stage instead of binding it positionally against a decoupled roster.

**Repository Touchpoints:** `server/adapters/mcp/vision/backends.py` (`_build_request_payload` ~`:846`; Gemini parts loop ~`:858-868`; OpenAI/OpenRouter content loop ~`:907-916`), `server/adapters/mcp/vision/prompting.py` (caption helper consumed by both paths and the `IMAGES` roster), `server/adapters/mcp/vision/backend.py` (`VisionImageInput` `path`/`role`/`label`/`media_type` ~`:17-24`)

**Acceptance Criteria:**
- In the `google_ai_studio` branch, every appended `{"inline_data": {...}}` part is immediately preceded by a `{"text": <caption>}` part for that same image; the single leading payload-text part stays first in the `parts` list.
- In the OpenAI/OpenRouter branch, every appended `{"type": "image_url", ...}` part is immediately preceded by a `{"type": "text", "text": <caption>}` part for that same image; the single leading payload-text part stays first in the `content` list.
- Each caption is deterministic for a given `VisionImageInput`: it names the `label`, the `role`, and the derivable view/stage only; it never emits raw coordinate tokens, absolute metric magnitudes, or chain-of-thought.
- Image ordering and `inline_data`/`image_url` encoding are otherwise unchanged; only the interleaved caption parts are added.
- No contract, schema, runner budget field, or parsing path changes.

## Implementation Notes

- The two transmit paths both live in `_build_request_payload` in
  `server/adapters/mcp/vision/backends.py`:
  - `google_ai_studio` builds `parts` starting with one
    `{"text": build_vision_payload_text(...)}` and then appends a bare
    `{"inline_data": {"mime_type": ..., "data": ...}}` per image in the loop at
    `:858-868`.
  - the OpenAI/OpenRouter path builds `content` starting with one
    `{"type": "text", "text": build_vision_payload_text(...)}` and then appends a
    bare `{"type": "image_url", "image_url": {"url": ...}}` per image in the loop
    at `:907-916`.
- The fix is to push a caption text part inside each loop body, BEFORE appending
  the blob, using the same per-image fields already in scope (`image.label`,
  `image.role`, and the view/stage tokens derivable from the label, e.g. a label
  like `target_front_after` yields `view=front | stage=after`). `VisionImageInput`
  exposes exactly `path`/`role`/`label`/`media_type` (`server/adapters/mcp/vision/backend.py:17-24`),
  so the caption is built purely from data already present at transmit time; no
  new field is introduced.
- The caption string itself is produced by a single shared helper that
  `TASK-174-02` extracts into `server/adapters/mcp/vision/prompting.py` and reuses
  for the flat `IMAGES`/`REFERENCE_IMAGES` roster (`:497`, `:539`, `:586`,
  `:629`, `:770`). This slice may inline a minimal local formatter first and then
  converge on the shared helper, or land both together; the parity proof in
  `TASK-174-02` requires a single source of truth for the format.
- Suggested caption shape (symbolic, single line):
  `"[image: <label> | role=<role> | view=<view> | stage=<stage>]"`, omitting
  `view`/`stage` tokens that cannot be derived rather than emitting placeholders.
- Relevant techniques to cite as design basis (advisory only; re-measure on
  Blender fixtures before claiming gains):
  - Set-of-Mark Prompting (arXiv:2310.11441) — explicit visual/textual marks per
    region/image sharply improve VLM grounding and attribution.
  - ViP-LLaVA (arXiv:2312.00784) — visual prompts and adjacent textual references
    let the model attend to the intended image region/identity.
  - VLM-Grounder (arXiv:2410.13860) — zero-shot 3D grounding benefits from
    image-level identity cues fed alongside each image rather than in a detached
    list.

## Pseudocode

```python
def _build_request_payload(self, request: VisionRequest) -> dict[str, Any]:
    vision_contract_profile = self._external_config.vision_contract_profile

    if self._external_config.provider_name == "google_ai_studio":
        parts: list[dict[str, Any]] = [
            {"text": build_vision_payload_text(request, ...)}
        ]
        for image in request.images:
            media_type = _media_type_for(image.path, image.media_type)
            encoded = base64.b64encode(Path(image.path).read_bytes()).decode("ascii")
            parts.append({"text": format_image_caption(image)})  # interleaved BEFORE blob
            parts.append({"inline_data": {"mime_type": media_type, "data": encoded}})
        return {"systemInstruction": {...}, "contents": [{"parts": parts}], "generationConfig": {...}}

    content: list[dict[str, Any]] = [
        {"type": "text", "text": build_vision_payload_text(request, ...)}
    ]
    for image in request.images:
        media_type = _media_type_for(image.path, image.media_type)
        content.append({"type": "text", "text": format_image_caption(image)})  # interleaved BEFORE blob
        content.append({"type": "image_url", "image_url": {"url": _image_to_data_url(image.path, media_type)}})
    # ... response_format / provider plumbing unchanged ...
    return payload
```

## Runtime / Security Contract Notes

- Captions are advisory grounding hints inside a VLM interpretation request.
  They do not make vision authoritative: findings stay `not_truth_source` /
  `requires_deterministic_checks_for_correctness`, and deterministic inspection /
  assertion / silhouette continue to own scene truth. Vision must not mark gates
  complete or unlock tools as a result of this change.
- Captions stay symbolic: label, role, and derivable view/stage only. No raw
  coordinate tokens (they regress LLM spatial reasoning), no absolute metric
  magnitudes (any size language must remain a proportional ratio vs a trusted
  reference anchor elsewhere), and no chain-of-thought (reasoning stays in the
  orchestrator).
- No Blender main-thread or addon work is touched; this is a pure
  request-payload construction change on the external backend, so no
  `capture_scene_state` / `restore_scene_state` interaction is involved.

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_external_backend.py` — extend the
  google_ai_studio payload-capture test (~`:820-878`) to assert that, for a
  multi-image request, each `contents[0]["parts"]` `inline_data` part is
  immediately preceded by a `{"text": ...}` caption naming that image; extend the
  openrouter/openai payload-capture test (~`:745-799`) to assert each
  `messages[1]["content"]` `image_url` part is immediately preceded by a
  `{"type": "text", ...}` caption.
- `tests/unit/adapters/mcp/test_vision_prompting.py` — assert the caption format
  is deterministic and symbolic (no coordinate/metric/CoT tokens).

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
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_external_backend.py tests/unit/adapters/mcp/test_vision_prompting.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py` (run when external transmit behavior is exercised against a live provider lane)

## Validation Category

- vision payload-grounding proof
