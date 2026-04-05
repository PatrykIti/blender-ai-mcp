# TASK-139-04-01: Unit and Integration Coverage for Profile Routing

**Parent:** [TASK-139-04](./TASK-139-04_Regression_Harness_And_Documentation_For_Contract_Profiles.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Add focused automated coverage for contract-profile selection and routing across
runtime config, prompting, parser, and external backend layers.

## Repository Touchpoints

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`

## Acceptance Criteria

- tests prove explicit override, auto-match, and fallback profile selection
- tests prove OpenRouter Google-family compare flows use the intended prompt/
  schema/parser profile
- tests prove prose/no-JSON outputs still fail loudly under the new routing

## Leaf Work Items

- add runtime-config tests for resolved contract-profile selection
- add prompting tests for profile-aware narrow compare routing
- add parsing/backend tests for OpenRouter Google-family compare failures and
  repairs

## Changelog Impact

- include in the parent follow-on changelog entry when shipped
