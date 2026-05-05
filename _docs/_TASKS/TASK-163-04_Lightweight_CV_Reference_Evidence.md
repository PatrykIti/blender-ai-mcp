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

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -k "reference_understanding_transport_roundtrip or reference_understanding_refresh_replaces_gate_slice" -q`
