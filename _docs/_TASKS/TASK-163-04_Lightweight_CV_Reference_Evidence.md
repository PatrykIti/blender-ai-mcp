# TASK-163-04: Lightweight CV Reference Evidence

**Status:** ✅ Done
**Priority:** 🔴 High
**Parent:** [TASK-163](./TASK-163_Vision_Orchestrator_Feedback_Strategy_Normalization_And_Optional_Perception_Adapters.md)
**Objective:** Add deterministic lightweight reference-image metrics that complement RU without becoming truth authority.
**Repository Touchpoints:** `server/adapters/mcp/areas/reference_feedback.py`, `server/adapters/mcp/areas/reference_understanding.py`, `server/adapters/mcp/contracts/reference.py`
**Acceptance Criteria:** server-owned heuristics add bounded `visual_metrics`; missing/weak images do not crash RU; evidence stays advisory-only.

## Completion Summary

- added deterministic lightweight metrics:
  - `edge_density`
  - `contour_count`
  - `polygonal_contour_ratio`
  - `dominant_color_count`
  - `silhouette_aspect_ratio`
  - `facet_likelihood`
- threaded those metrics into RU augmentation and compact evidence summaries
- hardened the helper against tiny or low-signal images so the public schema
  never emits invalid numeric values

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/vision/test_reference_understanding_runtime_surface.py`

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`

## Changelog Impact

- covered by [318. TASK-163 reference orchestrator feedback core](../_CHANGELOG/318-2026-05-05-task-163-reference-orchestrator-feedback-core.md)

## Status / Board Update

- tracked under the open `TASK-163` umbrella
- does not become its own board row

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -k "reference_orchestrator_feedback_transport_surface or reference_understanding_transport_roundtrip or reference_understanding_refresh_replaces_gate_slice" -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_understanding_runtime_surface.py -k "reference_orchestrator_feedback_surface_with_real_blender_capture" -q`
