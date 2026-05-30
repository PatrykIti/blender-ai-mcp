# 385. TASK-181-04 scene-graph scope-drift regression lane

Date: 2026-05-30

## Summary

Implemented `TASK-181-04`: a deterministic, unit-level regression lane guarding
the squirrel Body+Head scope-drift failure class (TASK-173). It proves the
scene-graph evidence cannot silently collapse to Body + Head — the graph diff
flags every absent appendage as missing and the relation-triplet serializer
surfaces the whole-assembly relations.

## Changes

- new `tests/unit/adapters/mcp/test_vision_scope_drift_regression.py`:
  - the graph diff reports all appendages (tail/ears/legs) missing and their
    expected attachment edges missing when only Body + Head are built
  - the relation-triplet serializer surfaces appendage relations as subjects, not
    just Body/Head
  - a fully built, attached whole creature yields a clean diff

## Tests

- the three regression assertions above; `ruff` clean; full `tests/unit` green
- the live end-to-end proof remains in
  `tests/e2e/vision/test_reference_guided_squirrel_quality_regression.py`

## Follow-on

`TASK-181-01` (make the part registry the canonical compare scope so the live
loop consumes this evidence to keep whole-assembly precedence) remains the deep
guided-flow rewrite this lane will ultimately defend.

## Research Basis

Text-Scene (arXiv:2509.16721) / 3DGraphLLM (arXiv:2412.18450): relation-graph
evidence over the whole assembly. Re-measure on `tests/fixtures/vision_eval`.
