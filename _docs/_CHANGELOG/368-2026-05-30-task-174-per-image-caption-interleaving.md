# 368. TASK-174 per-image caption interleaving

Date: 2026-05-30

## Summary

Implemented the first Vision Output Quality slice (`TASK-174`): the external
vision backend now interleaves a deterministic, symbolic identity caption
immediately before each transmitted image, in both the Google `inline_data`
path and the OpenAI/OpenRouter `image_url` path. Previously images were sent as
bare blobs with their view/role identity living only in a decoupled flat
`IMAGES` roster, forcing the model to bind the Nth blob positionally and risking
front/side or before/after/reference mis-attribution that corrupts every
downstream finding.

## Changes

- added a shared caption helper in `server/adapters/mcp/vision/prompting.py`
  (`format_image_caption` / `format_image_roster_line`) that renders one stable
  format, e.g. `[image: target_front_after | role=after | view=front]`, derived
  only from the image `label`/`role` plus a canonical view token parsed from the
  label; the before/after stage is intentionally not echoed because it is
  already carried by `role` and the label text
- the caption stays symbolic by design: no raw coordinates, no absolute metric
  magnitudes, and no chain-of-thought (those regress VLM spatial reasoning and
  are reserved for the orchestrator)
- de-duplicated the five roster builders, which all now route through
  `format_image_roster_line`, so the flat roster line and the interleaved
  per-image caption share exactly one format and the model sees a consistent
  identity string in both places
- `server/adapters/mcp/vision/backends.py` `_build_request_payload` now appends
  a caption text part immediately before each `inline_data` (Google) and each
  `image_url` (OpenAI/OpenRouter) part; this is a payload-only change with no
  contract, schema, runner-budget, or parsing change
- runtime boundary unchanged: captions are advisory grounding hints inside a
  VLM interpretation request; vision stays `not_truth_source` and deterministic
  inspection/assertion/silhouette still own scene truth

## Tests

- `tests/unit/adapters/mcp/test_vision_prompting.py`: caption format is
  deterministic/symbolic, omits underivable tokens, and the roster reuses the
  caption format
- `tests/unit/adapters/mcp/test_vision_external_backend.py`: caption-then-blob
  parity walk over the captured request payload for both the OpenAI/OpenRouter
  (`messages[1]["content"]`) and Google (`contents[0]["parts"]`) paths
- full `poetry run pytest ./tests/unit` green (3516 passed); `ruff` and `mypy`
  clean on the touched modules

## Research Basis

Set-of-Mark (arXiv:2310.11441), ViP-LLaVA (arXiv:2312.00784), and VLM-Grounder
(arXiv:2410.13860) — image-level identity cues fed alongside each image sharply
improve VLM grounding and attribution. Absolute gains are to be re-measured on
`tests/fixtures/vision_eval` before any are claimed.
