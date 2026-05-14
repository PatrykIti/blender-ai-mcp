# TASK-140-05-02: Provider Notes, Env Example, and Launcher / Client Config Alignment

**Parent:** [TASK-140-05](./TASK-140-05_Regression_Harness_Provider_Notes_And_Operator_Guidance_For_Expanded_Profiles.md)
**Depends On:** [TASK-140-05-01](./TASK-140-05-01_Automated_Coverage_And_Harness_Scenario_Expansion.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Align `_docs/_VISION`, MCP client examples, `.env.example`, and launch helpers
with the expanded external profile matrix so operator guidance matches the real
runtime.

## Repository Touchpoints

- `.env.example`
- `scripts/run_streamable_openrouter.sh`
- `scripts/vision_harness.py`
- `tests/unit/scripts/test_script_tooling.py`
- `README.md`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Acceptance Criteria

- every documented family/profile path uses the same env/config vocabulary as
  runtime code
- `.env.example` and client examples stay aligned with promoted families
- launcher scripts do not hard-code stale profile assumptions after runtime
  expansion

## Implementation Notes

- keep `.env.example`, launcher helpers, and MCP client examples aligned with
  the same `vision_contract_profile` vocabulary exposed by runtime
- treat launcher/client config wording as documentation of the current matrix,
  not as a place to invent unsupported profile combinations
- coordinate this leaf with the coverage/evidence leaf so docs only promote
  profile paths backed by actual runtime evidence

## Runtime / Security Contract Notes

- do not let env examples or launcher helpers imply support that runtime has
  not actually earned
- keep provider/api-key examples bounded and avoid teaching unsafe inline
  secret handling patterns

## Docs To Update

- `.env.example`
- `README.md`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Tests To Add/Update

- `tests/unit/scripts/test_script_tooling.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/scripts/test_script_tooling.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Status / Board Update

- remains nested under `TASK-140-05`
- should close before provider notes or launch helpers are treated as current
  support truth
