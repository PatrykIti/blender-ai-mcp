# TASK-139-04-01: Unit and Targeted Integration Coverage for Profile Routing

**Parent:** [TASK-139-04](./TASK-139-04_Regression_Harness_And_Documentation_For_Contract_Profiles.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Add focused automated coverage for contract-profile selection and routing across
runtime config, prompting, parser, and external backend layers, including one
targeted compare-loop integration/e2e seam in `tests/e2e/vision/`.

This leaf intentionally owns the automated regression seam for profile routing:

- fast unit coverage in `tests/unit/adapters/mcp/`
- targeted compare-loop integration/e2e coverage in `tests/e2e/vision/`

Harness/script alignment and provider-note/documentation evidence stay on the
parent `TASK-139-04` slice and on
`TASK-139-04-02_Harness_Evidence_Provider_Notes_And_Operator_Guidance`.

## Repository Touchpoints

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/e2e/vision/`

## Acceptance Criteria

- unit tests prove explicit override, auto-match, and fallback profile
  selection
- unit tests prove OpenRouter Google-family compare flows use the intended
  prompt/schema/parser profile
- unit tests prove prose/no-JSON outputs still fail loudly under the new
  routing
- targeted automated compare-loop coverage in `tests/e2e/vision/` proves the
  selected contract profile is exercised end-to-end on the affected external
  path without relying only on harness/manual evidence

## Leaf Work Items

- add runtime-config tests for resolved contract-profile selection
- add prompting tests for profile-aware narrow compare routing
- add parsing/backend tests for OpenRouter Google-family compare failures and
  repairs
- add or update one focused `tests/e2e/vision/` scenario that validates the
  contract-profile-sensitive compare path at the workflow boundary

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- focused `tests/e2e/vision/` compare-loop coverage

## Changelog Impact

- include in the parent follow-on changelog entry when shipped

## Status / Board Update

- keep board tracking on the parent regression/docs slice unless this leaf is
  promoted independently
- when this leaf closes, update the parent task summary so it is explicit that
  this child covered automated unit plus targeted compare-loop integration/e2e
  regressions, while harness/provider-note documentation evidence remains
  tracked separately
