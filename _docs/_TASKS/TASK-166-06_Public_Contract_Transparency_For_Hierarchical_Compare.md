# TASK-166-06: Public Contract Transparency For Hierarchical Compare

**Parent:** [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Expose additive packet provenance, pass status, conflict notes, and budget diagnostics on the existing staged compare / iterate contracts while keeping `reference_orchestrator_feedback` as the compact orchestration-facing owner seam.

## Repository Touchpoints

- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/reference_planner.py`
- `server/adapters/mcp/areas/reference_feedback.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`

## Implementation Notes

- Additive only: existing staged compare / iterate fields stay in place and
  remain readable by current clients.
- Richer packet detail should be profile-aware:
  - omitted by default in compact flows unless failure or uncertainty makes it
    necessary
  - included in `preset_profile="rich"` and on compare uncertainty/failure
- `compare_diagnostics` must extend the current staged surfaces instead of
  duplicating `silhouette_analysis`, `part_segmentation`, `planner_detail`, or
  `budget_control`.
- The compact orchestrator path remains `reference_orchestrator_feedback`; rich
  packet diagnostics are an additive explanation surface, not a bypass around
  that read model.
- Any new provenance or authority wording must align with the existing repo
  boundary/gate vocabulary and the shipped `advisory_only` sidecar semantics.

## Acceptance Criteria

- `correction_candidates` can carry packet-aware provenance/evidence without
  renaming or removing the existing candidate fields.
- staged compare / iterate responses can expose additive `compare_diagnostics`
  with packet ids, pass status, conflict notes, and per-run budget detail.
- compact orchestrator feedback can project packet uncertainty/provenance at
  summary level without requiring the caller to parse raw packet diagnostics.
- uncertainty and packet conflicts are surfaced explicitly instead of being
  silently collapsed.
- detailed budget visibility remains additive and does not replace the existing
  `budget_control` operator surface.

## Tests To Add/Update

- staged compare / iterate contract-shape tests for additive diagnostics fields
- profile-behavior tests covering compact omission, rich inclusion, and
  failure/uncertainty auto-inclusion
- `reference_orchestrator_feedback` projection tests for packet uncertainty and
  budget pressure summaries

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- include in the umbrella `_docs/_CHANGELOG/` entry when the transparency
  contract ships

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
