# 351. TASK-168 orchestrator confinement closeout

Date: 2026-05-14

## Summary

Closed the `TASK-168` family end to end:

- `llm-guided` now enforces one profile-bound confinement contract across
  direct and router-corrected mutators, including phase/role/role-group
  fail-closed shielding, `checkpoint_iterate` mutation barriers, and no-match
  guided-manual heuristic suppression
- staged compare / iterate now keep external controllers on the existing
  packet-scoped, additive public seams by default: active-workset-first packet
  routing, compact `reference_orchestrator_feedback`, and richer detail only
  when `preset_profile="rich"` or uncertainty justifies escalation
- prompt and operator docs now say explicitly that
  `router_get_status().surface_profile` / `contract_version` plus the live
  `guided_flow_state` / `reference_orchestrator_feedback` projection outrank
  stale external memory and old tool schemas

## Runtime Surface

- guided execution policy and state-machine enforcement remain on the shipped
  owner seams:
  - `server/adapters/mcp/router_helper.py`
  - `server/adapters/mcp/session_capabilities_flow.py`
  - `server/adapters/mcp/session_capabilities_registry.py`
  - `server/adapters/mcp/session_capabilities_runtime_glue.py`
- compare/iterate confinement remains on the existing staged reference owners:
  - `server/adapters/mcp/areas/reference.py`
  - `server/adapters/mcp/areas/reference_compare_packets.py`
  - `server/adapters/mcp/areas/reference_planner.py`
  - `server/adapters/mcp/areas/reference_feedback.py`
- the closeout docs pass adds the final authority-line wording on the existing
  public prompt and operator seams rather than introducing a second session
  manifest wrapper

## Docs And Governance

- updated:
  - `README.md`
  - `_docs/_MCP_SERVER/README.md`
  - `_docs/_PROMPTS/README.md`
  - `_docs/_PROMPTS/GUIDED_SESSION_START.md`
  - `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
  - `_docs/_PROMPTS/REFERENCE_GUIDED_ARCHITECTURE_BUILD.md`
  - `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
  - `tests/unit/adapters/mcp/test_public_surface_docs.py`
- moved `TASK-168` from the promoted `To Do` board section to `Done`
- closed the nested `TASK-168-*` task files administratively under the umbrella

## Validation

- focused owner-lane unit proof:
  - `PYTHONPATH=. poetry run pytest tests/unit/router/application/test_router_handler_parameters.py tests/unit/router/application/test_workflow_triggerer.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_router_elicitation.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_context_bridge.py tests/unit/router/application/test_supervisor_router.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/router/application/test_router_contracts.py tests/unit/adapters/mcp/test_prompt_catalog.py tests/unit/adapters/mcp/test_prompt_provider.py tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
  - result: `476 passed`
- broad repo unit proof:
  - `PYTHONPATH=. poetry run pytest ./tests/unit`
  - result: `3432 passed`
- repo-wide quality gates:
  - `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  - result: passed
- repo-supported Blender E2E runner:
  - `poetry run python scripts/run_e2e_tests.py`
  - result: `477 passed, 3 skipped`
