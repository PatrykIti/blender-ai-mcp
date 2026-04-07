# TASK-146-03: Qwen OpenRouter Structured Output Verification And Profile Hardening

**Parent:** [TASK-146](./TASK-146_Guided_Runtime_Guardrails_Vision_Profile_And_Prompting_Hardening.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Depends On:** [TASK-140](./TASK-140_Expand_External_Vision_Contract_Profiles_Across_Qwen_Anthropic_OpenAI_And_NVIDIA.md)

## Objective

Verify against official documentation how the active Qwen/OpenRouter path
should request and enforce structured JSON output, then harden the repo's
profile/config/runtime path around those documented requirements instead of
guessing from current model behavior.

## Repository Touchpoints

- `server/adapters/mcp/vision/`
- `server/adapters/mcp/contracts/`
- external provider/profile config
- `_docs/_VISION/README.md`
- real/fixture-backed compare-path tests

## Acceptance Criteria

- the task records the relevant official-doc findings for Qwen/OpenRouter
  structured output
- the active profile/config/runtime path is aligned with those findings
- tests cover the repaired/verified behavior as far as the repo can assert it
- docs clearly distinguish:
  - what the provider/model officially supports
  - what the repo now requests
  - what still remains model-quality risk rather than config drift

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- any provider/profile notes that currently overstate or understate Qwen support

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/e2e/vision/`

## Changelog Impact

- include in the parent TASK-146 changelog entry when shipped

## Status / Board Update

- nested under TASK-146 as the external structured-output verification slice
