# 296. TASK-157 quality-gate scope and reference-refresh regressions

Date: 2026-05-03

## Summary

- stopped local-scope `scene_relation_graph(...)` verification from overwriting
  session-wide gates that are outside the inspected scope, so partial
  body/tail or subassembly checks no longer flip unrelated required-part or
  seam gates and then poison `final_completion`
- fixed guided mutation invalidation for `target_kind="object_role"` gates by
  resolving affected object names through the guided part registry instead of
  only matching against the role label string
- changed reference-understanding refresh to replace the previously tracked
  reference gate slice instead of appending to it, which now removes obsolete
  blockers and updates matching gate payloads when the active reference set
  changes under the same guided goal
- added focused unit regressions plus transport coverage for the refreshed
  reference-understanding slice over stdio and Streamable HTTP

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_reference_images.py -q`
  - result on this machine: `95 passed`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py -q`
  - result on this machine: `41 passed`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -k 'reference_understanding_transport_roundtrip or reference_understanding_refresh_replaces_gate_slice' -q`
  - result on this machine: `2 passed, 2 skipped, 6 deselected`
- `git diff --check`
