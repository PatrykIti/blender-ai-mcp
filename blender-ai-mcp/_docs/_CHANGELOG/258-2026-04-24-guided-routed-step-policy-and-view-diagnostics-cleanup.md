# 258. Guided routed-step policy and view diagnostics cleanup

Date: 2026-04-24

## Summary

Fixed three runtime correctness gaps in guided routing and USER_PERSPECTIVE
view diagnostics.

## What Changed

- in `server/adapters/mcp/router_helper.py`:
  - validate guided execution and naming policy for every corrected routed step
    before dispatching any step
  - strip MCP-only `guided_role` and `role_group` params before calling
    application handlers through `ToolDispatcher`
- in `blender_addon/application/handlers/scene.py`:
  - restore the original scene camera and remove the temporary USER_PERSPECTIVE
    diagnostics camera if mirroring fails before the caller receives the temp
    camera reference
- in `tests/unit/adapters/mcp/test_context_bridge.py` and
  `tests/unit/tools/scene/test_viewport_control.py`:
  - added regressions for corrected-step policy validation, guided policy-param
    stripping, and temp camera cleanup on mirror failure

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_context_bridge.py tests/unit/tools/scene/test_viewport_control.py -q -k "strips_guided_policy_params or validates_every_corrected_step or cleans_temp_camera_when_view_copy_fails"`
  - result on this machine: `3 passed`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_context_bridge.py tests/unit/tools/scene/test_viewport_control.py -q`
  - result on this machine: `40 passed`
- `PYTHONPATH=. poetry run pytest tests/unit/tools/test_mcp_area_main_paths.py tests/unit/adapters/mcp/test_context_bridge.py tests/unit/tools/scene/test_viewport_control.py -q`
  - result on this machine: `57 passed`
- `poetry run ruff check server/adapters/mcp/router_helper.py blender_addon/application/handlers/scene.py tests/unit/adapters/mcp/test_context_bridge.py tests/unit/tools/scene/test_viewport_control.py`
  - result on this machine: passed
- `poetry run mypy`
  - result on this machine: passed
- `PYTHONPATH=. poetry run pytest tests/unit -q`
  - result on this machine: `3092 passed`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  - result on this machine: passed
