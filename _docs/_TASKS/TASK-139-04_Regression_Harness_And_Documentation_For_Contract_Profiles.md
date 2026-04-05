# TASK-139-04: Regression Harness and Documentation for Vision Contract Profiles

**Parent:** [TASK-139](./TASK-139_Model_Family_Specific_Vision_Contract_Profiles_For_External_Runtimes.md)
**Depends On:** [TASK-139-01](./TASK-139-01_Runtime_Contract_Profile_Model_And_Resolution.md), [TASK-139-02](./TASK-139-02_Prompt_Schema_And_Request_Routing_By_Contract_Profile.md), [TASK-139-03](./TASK-139-03_Parser_Repair_And_Diagnostics_By_Contract_Profile.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Prove the new vision-contract-profile routing with focused automated coverage
and document provider/model evidence in a way that distinguishes harness-ranked
results from operator-reported instability.

This slice intentionally splits into:

- automated regression coverage:
  - unit seams in `tests/unit/adapters/mcp/`
  - targeted compare-loop integration/e2e coverage in `tests/e2e/vision/`
- harness/doc/operator-guidance alignment:
  - harness config and evidence framing
  - provider/model notes
  - client/runtime documentation

## Business Problem

The repo already documents provider/model status, but the evidence story is
still mixed:

- some models are scored in the harness
- some failures are operator-reported
- the docs do not yet clearly connect those observations back to the selected
  vision contract profile

This task should keep the evidence chain explicit so runtime policy and docs do
not drift apart.

## Repository Touchpoints

- `scripts/vision_harness.py`
- `scripts/run_streamable_openrouter.sh`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/unit/scripts/test_script_tooling.py`
- `tests/e2e/vision/`
- `_docs/_VISION/README.md`
- `_docs/_VISION/HYBRID_LOOP_REAL_CREATURE_EVAL.md`
- `_docs/_VISION/REFERENCE_GUIDED_CREATURE_TEST_PROMPT.md`
- `_docs/_VISION/CROSS_DOMAIN_REFINEMENT_ROUTING_EVAL.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `README.md`

## Acceptance Criteria

- focused automated coverage proves the vision-contract-profile-selection
  behavior at both unit and targeted compare-loop integration/e2e seams
- the harness config/build path exposes the same vision-contract-profile
  assumptions as the runtime/docs path
- operator-facing launch helpers and their script coverage expose the same
  vision-contract-profile assumptions as the runtime/docs path
- provider notes and ranking guidance distinguish harness evidence from
  operator-reported instability
- vision eval/operator-guidance docs stay aligned with the same
  vision-contract-profile assumptions as the provider-note and harness guidance
  path
- docs explain the selected-vision-contract-profile behavior well enough that
  OpenRouter Google-family models are no longer treated as mysterious provider
  failures

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_VISION/HYBRID_LOOP_REAL_CREATURE_EVAL.md`
- `_docs/_VISION/REFERENCE_GUIDED_CREATURE_TEST_PROMPT.md`
- `_docs/_VISION/CROSS_DOMAIN_REFINEMENT_ROUTING_EVAL.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `README.md`

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
| 1 | [TASK-139-04-01](./TASK-139-04-01_Unit_And_Integration_Coverage_For_Profile_Routing.md) | Add focused automated coverage for runtime, prompting, backend, and parser vision-contract-profile routing across unit plus targeted compare-loop integration/e2e seams |
| 2 | [TASK-139-04-02](./TASK-139-04-02_Harness_Evidence_Provider_Notes_And_Operator_Guidance.md) | Align harness evidence, provider notes, and operator guidance with the new vision-contract-profile model |
