# TASK-166-06: Public Contract Transparency For Hierarchical Compare

**Parent:** [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md)
**Status:** 🚧 In Progress
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
- On `reference_compare_stage_checkpoint(...)`, `compare_diagnostics` should
  live top-level on the staged compare response.
- On `reference_iterate_stage_checkpoint(...)`, `compare_diagnostics` should
  also be reachable top-level on the iterate response; the nested compact
  `compare_result` may remain slim and is not the required access path for
  forced failure/uncertainty diagnostics.
- `compare_diagnostics` must extend the current staged surfaces instead of
  duplicating `silhouette_analysis`, `part_segmentation`, `planner_detail`, or
  `budget_control`.
- The compact orchestrator path remains `reference_orchestrator_feedback`; rich
  packet diagnostics are an additive explanation surface, not a bypass around
  that read model.
- Extend `server/adapters/mcp/areas/reference_feedback.py`'s existing typed
  staged-input path so `compare_diagnostics`, `budget_control`, and any
  packet-uncertainty summary fields arrive as first-class typed inputs
  alongside the current planner and correction-candidate contracts.
- Compact projection rules should stay explicit:
  - packet rationale / bounded provenance -> `evidence_summary`
  - packet conflicts, skipped ranking, and budget clipping -> `uncertainty_notes`
  - merged actionable packet outputs -> `correction_focus`
  - if packet/budget uncertainty changes the recommended next step, the existing
    message/next-action path carries that guidance
- Any new provenance or authority wording must align with the existing repo
  boundary/gate vocabulary and the shipped `advisory_only` sidecar semantics.
- Deferred owner-seam follow-on from the 2026-05-10 backend repair:
  `server/adapters/mcp/vision/parsing.py` owns packet guidance normalization,
  `server/adapters/mcp/vision/backends.py` only forwards parsed
  `packet_guidance`, and any broader typed projection cleanup across backend /
  runner / public transparency seams should be handled here without duplicating
  status or ranking heuristics in provider backends.

## Pseudocode

```text
compare_diagnostics = build_compare_diagnostics(packet_results, budget_state)
staged_compare = attach_compare_diagnostics(compare_result, compare_diagnostics)
iterate = attach_compare_diagnostics(iterate_result, compare_diagnostics)
compact_feedback = project_compare_diagnostics_into_feedback(
  compare_diagnostics,
  budget_control,
  correction_candidates,
)
```

## Runtime / Security Contract Notes

- `compare_diagnostics` is additive and profile-aware; it must not create a
  second public response family or bypass the compact `reference_orchestrator_feedback`
  seam.
- Failure/uncertainty diagnostics need one unambiguous surfaced path on both
  staged compare and staged iterate responses.
- Provenance/budget detail must remain bounded and transport-safe; do not leak
  raw internal packet logs or unredacted runtime payloads.

## Acceptance Criteria

- `correction_candidates` can carry packet-aware provenance/evidence without
  renaming or removing the existing candidate fields.
- staged compare / iterate responses can expose additive `compare_diagnostics`
  with packet ids, pass status, conflict notes, and per-run budget detail.
- compact iterate responses have one unambiguous access path for forced
  failure/uncertainty diagnostics even when nested `compare_result` stays slim.
- compact orchestrator feedback can project packet uncertainty/provenance at
  summary level without requiring the caller to parse raw packet diagnostics.
- uncertainty and packet conflicts are surfaced explicitly instead of being
  silently collapsed.
- detailed budget visibility remains additive and does not replace the existing
  `budget_control` operator surface.

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_reference_compare_packets.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- staged compare / iterate contract-shape tests for additive diagnostics fields
- profile-behavior tests covering compact omission, rich inclusion, and
  failure/uncertainty auto-inclusion
- `reference_orchestrator_feedback` projection tests for packet uncertainty and
  budget pressure summaries
- integration/transport proof on `tests/e2e/integration/test_guided_gate_state_transport.py`
  when staged compare / iterate payload shape changes for client-visible flows

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- record transparency changes through incremental TASK-166 changelogs; the
  2026-05-10 backend packet-guidance normalizer repair is tracked in entry
  `333`, while broader owner-seam cleanup remains deferred under this subtask

## Status / Board Update

- keep parent `TASK-166`, this subtask, and the promoted board row aligned in
  `_docs/_TASKS/README.md`
- when this subtask closes, record whether transport/integration proof shipped
  in the same branch or remains explicit follow-on work

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`
