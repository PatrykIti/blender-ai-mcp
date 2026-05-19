# 356. TASK-169 reference-guided quality drift regression and runtime authority

Date: 2026-05-19

## Summary

TASK-169 closes the remaining low-poly squirrel quality-drift gap across unit, integration, and Blender-backed proof lanes. The closeout set:

- keeps guided creature compare broad-first on primary masses (`Body + Head`, `Tail`) during early form-finding before local blocker packets dominate
- keeps global creature quality quality bars authoritative over local gate progress
- hardens guided `call_tool(name="scene_get_viewport", ...)` contract tolerance so legacy `output_mode="IMAGE_PATH"` now maps deterministically to `FILE` on the guided proxy path while direct visible `scene_get_viewport(...)` remains canonical and strict
- refreshes session/reference-understanding handoff and evidence surfaces so local seam progress cannot hide stale one-reference state
- stabilizes the stdio reconnect timeout budget used by the repo-supported E2E transport proof so the full closeout runner no longer flakes during legacy-flat MCP session startup
- finalizes task-board/changelog/docs coherence for the completed umbrella and descendants

## Validation

- focused owner-lane unit proof:
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_search_surface.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_mcp_viewport_output.py -q`
- focused guided integration and Blender-backed proof:
  - `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py tests/e2e/router/test_guided_manual_handoff.py tests/e2e/vision/test_goal_derived_gate_creature_completion.py tests/e2e/vision/test_reference_guided_squirrel_quality_regression.py -q`
- targeted Blender-backed proof lane:
  - `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_guided_squirrel_quality_regression.py -q`
- closeout governance proof:
  - `git diff --check`
  - `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  - `PYTHONPATH=. poetry run pytest ./tests/unit`
  - `poetry run python scripts/run_e2e_tests.py`
  - `_docs/_TASKS/README.md` and `TASK-169-...` task statuses aligned with runtime/delivery evidence
