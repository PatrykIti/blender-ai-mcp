# 356. TASK-169 reference-guided quality drift regression and runtime authority

Date: 2026-05-19

## Summary

TASK-169 closes the remaining low-poly squirrel quality-drift gap across unit, integration, and Blender-backed proof lanes. The closeout set:

- keeps guided creature compare broad-first on primary masses (`Body + Head`, `Tail`) during early form-finding before local blocker packets dominate
- keeps global creature quality quality bars authoritative over local gate progress
- hardens `scene_get_viewport(...)` contract tolerance so legacy `output_mode="IMAGE_PATH"` now maps deterministically to `FILE`
- refreshes session/reference-understanding handoff and evidence surfaces so local seam progress cannot hide stale one-reference state
- finalizes task-board/changelog/docs coherence for the completed umbrella and descendants

## Validation

- focused owner-lane unit proof:
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_search_surface.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_mcp_viewport_output.py -q`
- targeted Blender-backed proof lane:
  - `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_guided_squirrel_quality_regression.py -q`
- closeout governance proof:
  - `git diff --check`
  - `_docs/_TASKS/README.md` and `TASK-169-...` task statuses aligned with runtime/delivery evidence
