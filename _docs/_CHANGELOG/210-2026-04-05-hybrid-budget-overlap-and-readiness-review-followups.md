# 210. Hybrid budget, overlap, and readiness review follow-ups

Date: 2026-04-05

## Summary

Closed a small review-follow-up bundle across the hybrid-loop budget path, the
mesh-aware contact truth path, and guided staged-session readiness.

## What Changed

- tightened the hybrid-loop model-name bias so Gemini names such as
  `gemini-2.5-flash` / `gemini-2.5-pro` are no longer downgraded through the
  `gemini`/`mini` substring collision
- preserved true overlap propagation in mesh-aware `scene_measure_gap(...)`, so
  mesh overlaps still report `relation="overlapping"` and
  `scene_assert_contact(..., allow_overlap=false)` continues to reject them as
  overlaps instead of flattening them into plain contact
- narrowed `guided_reference_readiness.pending_reference_count` to
  goal-relevant pending refs for the active staged session, so stale pending
  refs for another goal do not block ready compare/iterate flows by themselves
- added focused regression coverage for:
  - Gemini-vs-mini budget bias and resulting pair/candidate budgets
  - mesh-overlap gap/contact semantics
  - ready-session staged readiness with unrelated pending refs
- updated product docs to clarify:
  - `pending_reference_count` semantics on the guided readiness contract
  - mesh-aware overlap rejection as a distinct truth condition
  - the model-aware budget note for Gemini vs explicit mini-tier names

## Why

These were narrow but important post-merge review findings. Left unfixed, they
would have:

- trimmed Gemini hybrid-loop payloads more aggressively than intended
- allowed real mesh overlaps to pass through the contact truth path too easily
- blocked ready staged compare/iterate sessions because of stale pending refs
  from another goal

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_session_phase.py tests/unit/tools/scene/test_scene_measure_tools.py tests/unit/tools/scene/test_scene_assert_tools.py -q`
