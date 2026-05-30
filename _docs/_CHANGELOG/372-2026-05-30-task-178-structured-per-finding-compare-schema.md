# 372. TASK-178 structured per-finding compare schema

Date: 2026-05-30

## Summary

Implemented `TASK-178`: the bounded compare output now carries an additive,
structured per-finding channel alongside the existing string lists, so a finding
can name the view that revealed it, the canonical scene part it concerns, an
axis/direction, and a PROPORTIONAL magnitude ratio versus a reference anchor —
instead of being an unbound prose string. Additive and backward compatible: the
string lists remain, the new `findings` array defaults to empty, and the narrow
Google-family compare schema is unchanged.

## Changes

- `server/adapters/mcp/sampling/result_types.py`: added `VisionFindingContract`
  (`finding`, `view_id`, `target_label`, `axis` x/y/z/none, `direction`
  increase/decrease/none, `magnitude_ratio`, `reference_id`, `confidence`) and a
  `findings: list[VisionFindingContract]` field on `VisionAssistContract`. The
  magnitude is documented as a proportional ratio, never an absolute measurement.
- `server/adapters/mcp/vision/prompting.py`: added a strict-mode `_FINDINGS_SCHEMA`
  (all properties required with nullable types so strict providers accept it) and
  wired `findings` into the default generic and packet compare response schemas
  and their expected-key tuples; the narrow `google_family_compare` schema stays
  minimal.
- `server/adapters/mcp/vision/parsing.py`: added `_coerce_findings_list`
  (drops malformed entries, clamps `confidence` to [0,1], keeps `magnitude_ratio`
  as a non-negative ratio, normalizes `axis`/`direction` to the allowed enums or
  null) and emit `findings` from the compare builder.

## Tests

- `tests/unit/adapters/mcp/test_vision_prompting.py`: the packet/default schemas
  expose the structured `findings` item properties and stay strict-mode valid
- `tests/unit/adapters/mcp/test_vision_parsing.py`: structured findings are
  coerced (enum normalization, confidence clamping, negative-ratio drop, malformed
  entries dropped) and default to an empty list when absent
- full `poetry run pytest ./tests/unit` green; `ruff` and `mypy` clean

## Follow-on

`TASK-178-03` planner/reporting propagation (using the structured findings to
drive correction ranking) remains a follow-on; the findings channel already
reaches the orchestrating LLM through the result envelope.

## Research Basis

SpatialRGPT (arXiv:2406.01584), SceneVerse (arXiv:2401.09340), GPTEval3D
(arXiv:2401.04092), SD-VLM (arXiv:2509.17664): per-finding view/object/axis
binding with proportional magnitudes improves an LLM's spatial grounding far more
than unbound prose. Re-measure on `tests/fixtures/vision_eval` before claiming
gains.
