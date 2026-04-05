# TASK-139-04: Regression Harness and Documentation for Contract Profiles

**Parent:** [TASK-139](./TASK-139_Model_Family_Specific_Vision_Contract_Profiles_For_External_Runtimes.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Prove the new contract-profile routing with focused unit/integration coverage
and document provider/model evidence in a way that distinguishes harness-ranked
results from operator-reported instability.

## Business Problem

The repo already documents provider/model status, but the evidence story is
still mixed:

- some models are scored in the harness
- some failures are operator-reported
- the docs do not yet clearly connect those observations back to the selected
  contract profile

This task should keep the evidence chain explicit so runtime policy and docs do
not drift apart.

## Repository Touchpoints

- `scripts/vision_harness.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/unit/scripts/test_script_tooling.py`
- `tests/e2e/vision/`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- focused unit/integration coverage proves the profile-selection behavior
- the harness config/build path exposes the same contract-profile assumptions as
  the runtime/docs path
- provider notes and ranking guidance distinguish harness evidence from
  operator-reported instability
- docs explain the selected-profile behavior well enough that OpenRouter
  Google-family models are no longer treated as mysterious provider failures

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/unit/scripts/test_script_tooling.py`
- focused `tests/e2e/vision/` compare-loop coverage

## Changelog Impact

- include in the parent umbrella changelog entry when shipped

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-139-04-01](./TASK-139-04-01_Unit_And_Integration_Coverage_For_Profile_Routing.md) | Add focused automated coverage for runtime, prompting, backend, and parser profile routing |
| 2 | [TASK-139-04-02](./TASK-139-04-02_Harness_Evidence_Provider_Notes_And_Operator_Guidance.md) | Align harness evidence, provider notes, and operator guidance with the new contract-profile model |
