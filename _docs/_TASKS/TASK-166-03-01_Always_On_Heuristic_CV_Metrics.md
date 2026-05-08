# TASK-166-03-01: Always-On Heuristic CV Metrics

**Parent:** [TASK-166-03](./TASK-166-03_Deterministic_CV_And_Optional_PyTorch_Perceiver_Sidecars.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High
**Objective:** Add always-on deterministic CV metrics using lightweight libraries such as OpenCV / scikit-image so the compare family gets compact structural evidence before broad LLM interpretation.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/vision/reference_support.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Implementation Notes

- Candidate metrics:
  - silhouette aspect ratio
  - contour count
  - polygonal contour ratio
  - edge density
  - connected components
  - bounded symmetry/coverage heuristics where justified

## Acceptance Criteria

- deterministic image metrics are available to packet compare
- these metrics stay compact and machine-readable
