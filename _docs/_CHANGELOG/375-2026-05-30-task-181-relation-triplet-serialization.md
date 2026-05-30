# 375. TASK-181 relation-triplet prompt serialization

Date: 2026-05-30

## Summary

Implemented the core of `TASK-181` (subtask `TASK-181-03`): the deterministic
scene relation graph is now serialized for the VLM prompt as symbolic
`subject relation object` triplets (contact / gap / overlap / symmetry /
alignment), never raw coordinates, because symbolic relations ground an LLM's
spatial reasoning far better than coordinate tokens. The compare packet prompt
gains a `SCENE_RELATIONS:` section, emitted only when relation pairs are present.

## Changes

- `server/adapters/mcp/vision/prompting.py`: added `serialize_relation_triplets`
  (per-subject k-capped, picks the single most informative relation per pair via
  `_dominant_relation_phrase`) and `_relation_triplet_lines_from_truth` (extracts
  pairs from `truth_summary['pairs']` or `truth_summary['relation_graph']['pairs']`).
  The packet compare prompt now adds a `SCENE_RELATIONS:` section when triplets
  exist; it is a no-op when the truth summary carries no relation graph.

## Tests

- `tests/unit/adapters/mcp/test_vision_prompting.py`: triplets are symbolic (no
  coordinate tokens), capped per subject, drop pairs without a subject or a
  derivable relation; the packet prompt includes `SCENE_RELATIONS` when present
  and omits it otherwise
- full `poetry run pytest ./tests/unit` green; `ruff` and `mypy` clean

## Follow-on

`TASK-181-01` (make the part registry the canonical compare scope to fix the
`TASK-173` Body+Head scope drift), `TASK-181-02` (typed graph-vs-graph diff
contract), and `TASK-181-04` (squirrel scope-drift regression lane) remain open;
they touch the deep staged-compare packet orchestration.

## Research Basis

3DGraphLLM (arXiv:2412.18450) and Text-Scene (arXiv:2509.16721): relation
triplets beat raw coordinates for LLM spatial reasoning (Text-Scene: relations
59.4 vs coords 18.4). SceneVerse (arXiv:2401.09340) for the relation taxonomy.
Re-measure on `tests/fixtures/vision_eval` before claiming gains.
