# TASK-146-05: Extended Realism Coverage For Guided Runtime Hardening

**Parent:** [TASK-146](./TASK-146_Guided_Runtime_Guardrails_Vision_Profile_And_Prompting_Hardening.md)
**Status:** ✅ Done
**Priority:** 🟠 High
**Depends On:** [TASK-146-01](./TASK-146-01_Workflow_Trigger_Boundaries_And_MCP_Guardrail_Coverage.md), [TASK-146-02](./TASK-146-02_Docker_Dependency_Group_And_Runtime_Packaging_Alignment.md), [TASK-146-03](./TASK-146-03_Qwen_OpenRouter_Structured_Output_Verification_And_Profile_Hardening.md), [TASK-146-04](./TASK-146-04_Search_First_Prompt_Library_And_Instruction_Surface_Hardening.md)

**Completion Summary:** Completed on 2026-04-07. Added the next realism-focused
coverage slice after the first TASK-146 hardening wave: transport-backed E2E
coverage now exercises the guided `search_tools(...)` / `call_tool(...)`
boundary, E2E router coverage now covers a broader direct-call matrix under
manual/no-match guided sessions, and opt-in smokes now exist for live
OpenRouter/Qwen structured-output behavior and Docker runtime dependency
availability. Supporting unit coverage and `_docs/_TESTS/README.md` were
updated in the same branch.

## Objective

Extend the first TASK-146 regression slice with more realistic coverage so the
hardening work is not defended only by unit tests and wording checks.

The goal here is to probe the repaired behavior from more than one side:

- transport-backed guided search/call behavior
- broader direct guided calls under real router fixtures
- live OpenRouter/Qwen behavior when explicitly enabled
- real Docker runtime dependency availability when explicitly enabled

## Repository Touchpoints

- `tests/e2e/integration/`
- `tests/e2e/router/`
- `tests/e2e/vision/`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `_docs/_TESTS/README.md`

## Acceptance Criteria

- transport-backed E2E coverage exists for the guided search-first boundary
- broader E2E coverage exists for direct guided calls that should not reopen
  workflows after manual/no-match handoff
- opt-in smoke coverage exists for:
  - live OpenRouter/Qwen structured JSON behavior
  - Docker runtime dependency availability
- `_docs/_TESTS/README.md` documents those new coverage slices and their env
  gates

## Docs To Update

- `_docs/_TESTS/README.md`

## Tests To Add/Update

- `tests/e2e/integration/test_guided_search_first_call_tool_boundary.py`
- `tests/e2e/router/test_guided_direct_calls_do_not_trigger_workflows.py`
- `tests/e2e/vision/test_openrouter_qwen_json_mode.py`
- `tests/e2e/integration/test_docker_runtime_vision_dependencies.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when this coverage slice ships

## Status / Board Update

- completed administratively under the already-closed TASK-146 umbrella
- kept as a historical execution leaf so the added realism coverage is visible
  in repo planning history
