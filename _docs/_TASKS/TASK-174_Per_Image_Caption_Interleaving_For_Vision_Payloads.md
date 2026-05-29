# TASK-174: Per-Image Caption Interleaving For Vision Payloads

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Vision / VLM Payload Grounding
**Estimated Effort:** Small
**Follow-on After:** [TASK-171](./TASK-171_Creature_Attachment_First_Build_Contract_And_Structured_Vision_Handoff.md), [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md)
**Related:** [TASK-140](./TASK-140_Expand_External_Vision_Contract_Profiles_Across_Qwen_Anthropic_OpenAI_And_NVIDIA.md), [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md), [_docs/_VISION/MULTI_VIEW_CAPTURE_PLAN.md](../_VISION/MULTI_VIEW_CAPTURE_PLAN.md)

## Relationship To Existing Board Items

- `TASK-171` shipped the attachment-first creature contract and the structured
  vision handoff that produces multi-view, multi-role capture bundles, so the
  request now routinely carries several before/after/reference blobs whose
  identity matters for every shape/proportion/reference finding.
- `TASK-172` shipped the optional vision capability runtime and the localized
  perception seam, but those advisory sidecars only help if the orchestrating
  LLM can already tell which blob is which view/role/stage; today it cannot,
  because images arrive as bare blobs with no adjacent caption.
- This umbrella is a STANDALONE family, not a child of `TASK-171`/`TASK-172`.
  It links those upstream families via **Follow-on After:** and **Related:**.
  Its own subtasks point at this umbrella via **Parent:**.
- This family deliberately does not reopen the `TASK-140-06`
  provider-capability substrate. It is a payload-only grounding fix inside the
  request-payload builder and the prompt roster helper.

## Objective

Make the external VLM bind each image blob to its correct view/role/stage
identity by interleaving a deterministic one-line caption text part immediately
BEFORE every image part in both transmit paths
(`google_ai_studio` inline_data and OpenAI/OpenRouter image_url). The flat
`IMAGES` roster stays as a redundant index. No contract change, no new
structured fields, no new behavior on the parsing side.

## Business Problem

In `server/adapters/mcp/vision/backends.py` the request-payload builder
(`_build_request_payload`, around `:846`) appends every image as a bare blob:

- the `google_ai_studio` branch pushes one leading `{"text": ...}` part and then
  appends each image as a bare `{"inline_data": {...}}` part (around `:849-868`),
  with no text part between images.
- the OpenAI/OpenRouter branch pushes one leading `{"type": "text", ...}` part
  and then appends each image as a bare `{"type": "image_url", ...}` part
  (around `:896-916`), again with no text between images.

The only place the view/role identity is described is the decoupled flat
`IMAGES` roster lines built in `server/adapters/mcp/vision/prompting.py`
(`f"- {image.role}: {image.label or image.role}"` at `:497`, `:539`, `:586`,
`:629`, `:770`). The roster lives entirely inside the leading text part and is
physically separated from the blobs.

The model must therefore bind the Nth blob to the Nth roster line purely
positionally. When the bundle interleaves before/after captures with multiple
references (the normal case after `TASK-171`), this positional binding
mis-attributes front vs side, before vs after, and render vs reference. Because
the per-image `VisionImageInput` already carries `role`
(`before`/`after`/`reference`) and a `label` that encodes the view/stage (for
example `target_front_after`), the identity information needed to caption each
blob is already present at transmit time and is simply being dropped on the
floor. Three independent analyses named this missing per-image grounding as the
single biggest hindrance to reliable 3D-scene understanding in this loop.

## Business Outcome

After this umbrella lands:

- every image blob in both providers is immediately preceded by a deterministic
  caption text part naming its label, role, and (when derivable) view/stage, so
  the orchestrating LLM no longer has to guess which blob is which.
- front/side, before/after, and render/reference attribution stops depending on
  blob ordering, which removes a whole class of corrupted shape, proportion, and
  reference findings at their source.
- the change is payload-only and fully backward compatible: the `IMAGES` roster
  remains as a redundant index, no contract gains a field, and the parsing /
  gate / scene-truth paths are untouched.

## Non-Goals

- Vision stays ADVISORY. Captions are still part of a VLM interpretation
  request; nothing here lets vision mark gates complete or unlock tools, and the
  resulting findings remain `not_truth_source` / `requires_deterministic_checks_for_correctness`.
  Deterministic inspection / assertion / silhouette continue to own scene truth.
- Do not introduce magnitudes as authoritative absolute measurements. Any size
  language a caption surfaces must stay a PROPORTIONAL RATIO against a trusted
  reference anchor, never an authoritative metric (VLMs land only ~37% within 2x
  on metric tasks).
- Do not turn on heavier perception sidecars (SAM/SAM2/GroundingDINO/Depth-Anything/CLIP/DINO).
  Those remain DEFAULT-OFF, advisory-only, packet-bounded per the `TASK-172`
  optional-runtime seam, and are out of scope here.
- Do not reopen the `TASK-140-06` provider-capability substrate.
- Do not emit raw coordinate tokens as primary evidence in the caption (raw
  coordinates hurt LLM spatial reasoning: 3DGraphLLM 50.1->42.6; Text-Scene
  relations 59.4 vs coords 18.4). Captions stay symbolic (label/role/view/stage);
  coordinates only on explicit demand elsewhere.
- Do not add VLM-side chain-of-thought for spatial judgments inside the caption
  (VSI-Bench regression of -1..-21%). All reasoning stays in the orchestrator.

## Execution Structure

| Order | Task | Purpose |
|------|------|---------|
| 1 | [TASK-174-01](./TASK-174-01_Caption_Interleaving_In_Both_Transmit_Paths.md) | Caption Interleaving In Both Transmit Paths |
| 2 | [TASK-174-02](./TASK-174-02_Caption_Helper_Payload_Parity_Tests_And_Docs.md) | Caption Helper, Payload Parity Tests And Docs |

## Repository Touchpoints

| Path / Module | Expected Ownership | Why It Is In Scope |
|---------------|--------------------|--------------------|
| `server/adapters/mcp/vision/backends.py` | request-payload builder (`_build_request_payload` ~`:846`; Gemini parts ~`:849-868`; OpenAI/OpenRouter content ~`:896-916`) | both transmit paths append bare image blobs with no adjacent caption; this is where the caption text part must be interleaved before each blob |
| `server/adapters/mcp/vision/prompting.py` | flat `IMAGES`/`REFERENCE_IMAGES` roster lines (~`:497`, `:539`, `:586`, `:629`, `:770`) | the roster is the only existing place the per-image identity is described; a shared caption helper extracted here keeps the roster and the interleaved captions in one format |
| `server/adapters/mcp/vision/backend.py` | `VisionImageInput` (`path`/`role`/`label`/`media_type`, ~`:17-24`) and `VisionRequest` (~`:27-36`) | the per-image identity fields the caption is built from already exist here; no field is added |
| `tests/unit/adapters/mcp/test_vision_external_backend.py`, `tests/unit/adapters/mcp/test_vision_prompting.py` | payload-shape and roster proof lanes | `test_vision_external_backend.py` already captures the outgoing `json` request payload (`captured["json"]`) and is the home for the caption-then-blob parity walk; `test_vision_prompting.py` already asserts roster text and owns the caption-format proof. `test_contract_payload_parity.py` validates Pydantic `MCPContract` construction, not request-payload shape, so it is out of scope for this slice |

## Test Matrix

| Slice | Primary Validation Lane | Why |
|------|--------------------------|-----|
| Gemini inline_data caption interleaving | `tests/unit/adapters/mcp/test_vision_external_backend.py` (google_ai_studio payload capture, ~`:820-878`) | already inspects `captured["json"]["contents"][0]["parts"]`, so it can assert a caption text part directly precedes each `inline_data` part |
| OpenAI/OpenRouter image_url caption interleaving | `tests/unit/adapters/mcp/test_vision_external_backend.py` (openrouter/openai payload capture, ~`:745-799`) | already inspects `captured["json"]["messages"][1]["content"]`, so it can assert a caption text part directly precedes each `image_url` part |
| caption helper + roster format parity | `tests/unit/adapters/mcp/test_vision_prompting.py` (and `tests/unit/adapters/mcp/test_vision_external_backend.py` for the interleaved captions) | proves the shared caption helper renders one stable format reused by both the roster and the interleaved captions |

## Acceptance Criteria

- In a multi-image request, the `google_ai_studio` payload alternates
  caption-then-blob: every `inline_data` part is immediately preceded by a
  `{"text": ...}` caption part naming that image, with one leading payload-text
  part still first.
- In a multi-image request, the OpenAI/OpenRouter payload alternates
  caption-then-blob: every `image_url` part is immediately preceded by a
  `{"type": "text", ...}` caption part naming that image, with one leading
  payload-text part still first.
- The caption is deterministic and symbolic for a given image (label, role, and
  derivable view/stage only); it contains no raw coordinate tokens, no absolute
  metric magnitudes, and no chain-of-thought.
- The flat `IMAGES` / `REFERENCE_IMAGES` roster remains present and uses the same
  caption format via the shared helper, so the roster stays a redundant index.
- No public contract gains or loses a field; parsing, gate, and scene-truth
  paths are unchanged; existing `tests/unit` and the vision e2e lanes still pass.
- Re-measure: cited benchmark gains are from indoor-scan / synthetic datasets,
  NOT Blender-vs-reference; before promoting any quality claim, re-measure
  absolute gains on the `tests/fixtures/vision_eval` golden fixtures.

## Docs To Update

- `_docs/_TASKS/README.md`
- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_VISION/MULTI_VIEW_CAPTURE_PLAN.md`

## Tests To Add/Update

- split across the execution slices below; each child task owns its exact lane

## Changelog Impact

- planning-only now; add a `_docs/_CHANGELOG/*` entry when the first slice lands
- do not treat this planning-only task creation as the changelog event

## Status / Board Update

- `_docs/_TASKS/README.md` should track `TASK-174` as an open item on the
  Vision / Hybrid Loop lane (board update owned by the coordinator)
- child tasks stay nested under the open umbrella and do not need board rows
  unless one later becomes a separately promoted follow-on

## Validation Commands

- `git diff --check`
- `rg -n "TASK-174|Per-Image Caption Interleaving For Vision Payloads|Caption Interleaving In Both Transmit Paths|Caption Helper, Payload Parity Tests And Docs" _docs/_TASKS/TASK-174*.md`

## Validation Category

- planning / governance / task-family definition
