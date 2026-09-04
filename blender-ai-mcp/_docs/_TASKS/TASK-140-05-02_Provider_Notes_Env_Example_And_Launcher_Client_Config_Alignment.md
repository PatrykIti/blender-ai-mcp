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
