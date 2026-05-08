# TASK-166-03-01: Always-On Heuristic CV Metrics

**Parent:** [TASK-166-03](./TASK-166-03_Deterministic_CV_And_Optional_PyTorch_Perceiver_Sidecars.md)  
**Status:** ✅ Done
**Priority:** 🔴 High
**Objective:** Add always-on deterministic CV metrics using lightweight libraries such as OpenCV / scikit-image so the compare family gets compact structural evidence before broad LLM interpretation.

## Completion Summary

- compare-time deterministic CV now reuses the existing silhouette/action-hint
  seam before packet compare execution, not only after the staged compare
  result is assembled
- packet-local `compare_diagnostics.packets[*].support_evidence` now carries a
  compact support-only summary derived from silhouette metrics and action hints
- packet extraction/ranking requests now receive those compact support-evidence
  summaries in packet metadata/payload before the LLM compare phase runs

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/reference_silhouette.py`
- `server/adapters/mcp/vision/silhouette.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_vision_silhouette.py`

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
- `server/adapters/mcp/vision/reference_support.py` remains the RU augmentation
  seam unless the repo deliberately expands it for compare-time sidecars later.

## Acceptance Criteria

- deterministic image metrics are available to packet compare
- these metrics stay compact and machine-readable
- CV-derived packet evidence is explicitly support-only and does not claim
  deterministic truth authority on its own

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_silhouette.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_stage_silhouette_contract.py -q`
- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_vision_silhouette.py`
- silhouette/CV owner-lane coverage for emitted metrics and compact machine
  readability
- `tests/e2e/vision/test_reference_stage_silhouette_contract.py`

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- include in the umbrella `_docs/_CHANGELOG/` entry when always-on compare-time
  CV metrics ship

## Status / Board Update

- keep parent `TASK-166` and this leaf aligned when compare-time heuristic CV
  closes or remains explicit follow-on scope
