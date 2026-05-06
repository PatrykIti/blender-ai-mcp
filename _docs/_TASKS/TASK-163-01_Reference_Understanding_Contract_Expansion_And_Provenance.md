# TASK-163-01: Reference Understanding Contract Expansion And Provenance

**Status:** ✅ Done
**Priority:** 🔴 High
**Parent:** [TASK-163](./TASK-163_Vision_Orchestrator_Feedback_Strategy_Normalization_And_Optional_Perception_Adapters.md)
**Objective:** Expand the typed RU contract with server-owned `views` and deterministic `visual_metrics` while preserving the advisory-only boundary.
**Repository Touchpoints:** `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/vision/prompting.py`, `server/adapters/mcp/vision/parsing.py`, `server/adapters/mcp/areas/reference_understanding.py`
**Acceptance Criteria:** RU payloads stay strict; `views` and `visual_metrics` are declared typed fields; no new public tool is introduced.

## Completion Summary

- added typed `views` and `visual_metrics` fields to
  `ReferenceUnderstandingSummaryContract`
- extended the RU prompt/schema path to accept `views`
- kept `visual_metrics` server-owned so deterministic image evidence can be
  added without making the VLM invent those numbers

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`

## Changelog Impact

- covered by [318. TASK-163 reference orchestrator feedback core](../_CHANGELOG/318-2026-05-05-task-163-reference-orchestrator-feedback-core.md)

## Status / Board Update

- closed historically under `TASK-163`; future related work should use an
  explicit follow-on task
- does not become its own board row

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_vision_parsing.py tests/unit/adapters/mcp/test_reference_images.py -q`
