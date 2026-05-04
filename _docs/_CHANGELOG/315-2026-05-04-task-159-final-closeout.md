# 315. TASK-159 final closeout

Date: 2026-05-04
Version: -

## Summary

- completed the remaining `TASK-159` scene MCP branches by extracting the
  spatial-graph/view-diagnostics, measure/assert, object-utility, and viewport
  execution logic out of `server/adapters/mcp/areas/scene.py` while keeping the
  file as the stable public facade
- completed the remaining addon scene branch by moving the Blender-side
  measurement/assertion cluster into
  `blender_addon/application/handlers/scene_measure_assert_mixin.py`
- closed the remaining reference-family admin/runtime drift by confirming the
  truth/planner split, hardening the reference-understanding E2E fake contexts,
  and aligning required-part gate verification for pending creature gates
- updated the runtime inventory audit so private helper modules under
  `server/adapters/mcp/areas/` are no longer treated as public MCP area
  surfaces, and aligned the facade-level `ctx_info` audit baseline with the new
  owner split
- closed task docs for `TASK-159`, `TASK-159-01`, `TASK-159-02`, `TASK-159-03`,
  and the remaining open leaves while moving the board entry from `In Progress`
  to `Done`

## Validation

- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`
