# TASK-166-03-01: Always-On Heuristic CV Metrics

**Parent:** [TASK-166-03](./TASK-166-03_Deterministic_CV_And_Optional_PyTorch_Perceiver_Sidecars.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High
**Objective:** Add always-on deterministic CV metrics using lightweight libraries such as OpenCV / scikit-image so the compare family gets compact structural evidence before broad LLM interpretation.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/reference_silhouette.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Implementation Notes

- Compare-time deterministic CV should extend the existing silhouette/action-hint
  seam first, because that is where staged compare currently emits heuristic
  image evidence.
- Candidate metrics:
  - silhouette aspect ratio
  - contour count
  - polygonal contour ratio
  - edge density
  - connected components
  - bounded symmetry/coverage heuristics where justified
- `vision/reference_support.py` remains the RU augmentation seam unless the repo
  deliberately expands it for compare-time sidecars later.

## Acceptance Criteria

- deterministic image metrics are available to packet compare
- these metrics stay compact and machine-readable
- CV-derived packet evidence is explicitly support-only and does not claim
  deterministic truth authority on its own

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
