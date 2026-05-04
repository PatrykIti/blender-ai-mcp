# 299. TASK-157 scope, dedupe, and compare-visibility regressions

Date: 2026-05-03

## Summary

- stopped scoped `scene_relation_graph(...)` checks from downgrading
  label-only `attachment_seam` and `support_contact` gates when the inspected
  object set does not contain the intended pair
- tightened gate staleness matching so label-based gates become `stale` after
  edits to matching object names such as `SquirrelTail`, instead of staying
  `passed` until an unrelated full refresh happens
- de-duplicated logically equivalent gates across proposal sources while
  preserving live verifier status/evidence on the surviving gate, and kept
  shared gates alive when the `reference_understanding` slice is later removed
- re-applied FastMCP visibility immediately after compare-time gate-plan
  persistence, so the visible repair/discovery surface matches the newly
  verified blockers in the same session step

## Validation

- `git diff --check`
- `python3 -m py_compile server/adapters/mcp/contracts/quality_gates.py server/adapters/mcp/transforms/quality_gate_verifier.py server/adapters/mcp/session_capabilities.py server/adapters/mcp/areas/reference.py`
- `poetry run mypy server/adapters/mcp/contracts/quality_gates.py server/adapters/mcp/transforms/quality_gate_verifier.py server/adapters/mcp/session_capabilities.py server/adapters/mcp/areas/reference.py`
  - result on this machine: `Success: no issues found in 4 source files`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_reference_images.py -q`
  - result on this machine: `109 passed`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -k 'later_goal_gate_proposal_preserves_reference_understanding_gates or same_call_goal_gate_proposal_preserves_reference_understanding_gates' -q`
  - result on this machine: `2 passed, 2 skipped, 10 deselected`
