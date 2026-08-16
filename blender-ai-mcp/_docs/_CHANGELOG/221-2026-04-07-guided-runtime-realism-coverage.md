# 221. Guided runtime realism coverage

Date: 2026-04-07

## Summary

Added the next realism-focused coverage slice after TASK-146 so the guided
runtime hardening is exercised by more than unit-only checks: transport-backed
E2E tests now cover the shaped search/call boundary, broader direct-call E2E
tests cover the repaired workflow-trigger boundary, and opt-in smokes exist
for live OpenRouter/Qwen behavior and Docker runtime dependency availability.

## What Changed

- added transport-backed E2E coverage for the search-first guided boundary:
  - `tests/e2e/integration/test_guided_search_first_call_tool_boundary.py`
- added broader E2E router coverage for direct guided calls that must not
  reopen workflows after manual/no-match handoff:
  - `tests/e2e/router/test_guided_direct_calls_do_not_trigger_workflows.py`
- added opt-in live OpenRouter/Qwen smoke coverage:
  - `tests/e2e/vision/test_openrouter_qwen_json_mode.py`
- added opt-in Docker runtime dependency smoke coverage:
  - `tests/e2e/integration/test_docker_runtime_vision_dependencies.py`
- extended runtime-config unit coverage for the new OpenRouter flags:
  - `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- updated `_docs/_TESTS/README.md` with the new targeted command and env-gated
  smoke-test instructions
- recorded this slice in task history as:
  - `TASK-146-05`

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py tests/e2e/integration/test_guided_search_first_call_tool_boundary.py tests/e2e/router/test_guided_direct_calls_do_not_trigger_workflows.py tests/e2e/vision/test_openrouter_qwen_json_mode.py tests/e2e/integration/test_docker_runtime_vision_dependencies.py -q`
- result: `32 passed, 5 skipped`
- `poetry run mypy`
- result: `Success: no issues found in 666 source files`

## Why

The first TASK-146 hardening wave fixed real runtime problems, but coverage was
still uneven: triggerer behavior had one good E2E, while OpenRouter/Qwen,
Docker runtime dependencies, and search-first MCP discipline were still mostly
defended by unit tests. This slice closes that gap with more realistic and more
operationally relevant coverage.
