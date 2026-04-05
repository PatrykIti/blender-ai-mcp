# TASK-139-04-01: Unit Coverage for Profile Routing

**Parent:** [TASK-139-04](./TASK-139-04_Regression_Harness_And_Documentation_For_Contract_Profiles.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Add focused unit coverage for contract-profile selection and routing across
runtime config, prompting, parser, and external backend layers.

This leaf intentionally owns the fast unit-test seam for profile routing.
Harness/script alignment and broader compare-loop integration evidence stay on
the parent `TASK-139-04` slice and on
`TASK-139-04-02_Harness_Evidence_Provider_Notes_And_Operator_Guidance`.

## Repository Touchpoints

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`

## Acceptance Criteria

- unit tests prove explicit override, auto-match, and fallback profile
  selection
- unit tests prove OpenRouter Google-family compare flows use the intended
  prompt/schema/parser profile
- unit tests prove prose/no-JSON outputs still fail loudly under the new
  routing

## Leaf Work Items

- add runtime-config tests for resolved contract-profile selection
- add prompting tests for profile-aware narrow compare routing
- add parsing/backend tests for OpenRouter Google-family compare failures and
  repairs

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped

## Status / Board Update

- keep board tracking on the parent regression/docs slice unless this leaf is
  promoted independently
- when this leaf closes, update the parent task summary so it is explicit that
  this child covered unit routing regressions, while harness/e2e evidence
  remains tracked separately
