# TASK-159-01-03: Reference Silhouette, View Diagnostics, And Understanding Sidecars

**Parent:** [TASK-159-01](./TASK-159-01_Reference_Area_Modularization_And_Checkpoint_Assembly_Boundaries.md)
**Status:** 🚧 In Progress
**Priority:** 🔴 High

## Objective

Extract the advisory-only silhouette, view-diagnostics, and
reference-understanding sidecars from `reference.py` without changing the
truth-vs-perception boundary.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- likely new helper modules such as:
  - `server/adapters/mcp/areas/reference_silhouette.py`
  - `server/adapters/mcp/areas/reference_view_diagnostics.py`
  - `server/adapters/mcp/areas/reference_understanding.py`
- `server/adapters/mcp/vision/`
- `tests/e2e/vision/test_reference_stage_silhouette_contract.py`
- `tests/e2e/vision/test_reference_understanding_runtime_surface.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`

## Current Code Anchors

- `_build_silhouette_analysis_payload(...)`
- `_select_silhouette_analysis_capture(...)`
- `_build_stage_view_diagnostics_hints(...)`
- `_build_view_diagnostics_hints(...)`
- `refresh_reference_understanding_summary_async(...)`
- `_blocked_reference_understanding_summary(...)`

## Planned Code Shape

```python
silhouette = build_silhouette_sidecar(...)
view_hints = build_view_diagnostics_sidecar(...)
understanding = refresh_reference_understanding(...)
```

## Runtime / Security Contract Notes

- keep silhouette and understanding outputs advisory; they must not become the
  authority for scene truth or gate completion
- preserve current trimming/redaction of provider payloads and debug fields
- keep current typed `reference_understanding_summary` and `silhouette_analysis`
  payload shapes stable

## Tests To Add/Update

- `tests/e2e/vision/test_reference_stage_silhouette_contract.py`
- `tests/e2e/vision/test_reference_understanding_runtime_surface.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_stage_silhouette_contract.py tests/e2e/vision/test_reference_understanding_runtime_surface.py tests/unit/adapters/mcp/test_contract_payload_parity.py -q`

## Docs To Update

- `_docs/_VISION/README.md` only if internal helper ownership is documented

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- silhouette/view-diagnostics/reference-understanding helpers no longer live as
  one inline cluster inside `reference.py`
- advisory sidecars preserve their current typed payloads and error behavior
- no extraction step blurs the truth/perception boundary

## Status / Board Update

- keep promoted tracking on parent `TASK-159`

## Progress Summary

As of 2026-05-04, the code split for this leaf has landed:

- `reference.py` now delegates advisory sidecars to:
  - `reference_silhouette.py`
  - `reference_view_diagnostics.py`
  - `reference_understanding.py`
- targeted unit lanes and contract payload checks are green
- one Blender-backed reference-understanding runtime E2E case still skipped
  because Blender RPC was unavailable at runtime, so this leaf stays
  `In Progress` until the closeout lane is fully green
