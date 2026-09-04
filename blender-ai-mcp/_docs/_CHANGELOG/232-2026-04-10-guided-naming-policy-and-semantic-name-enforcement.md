# 232. Guided naming policy and semantic name enforcement

Date: 2026-04-10

## Summary

Completed TASK-154 by moving guided object naming from prompt-only guidance and
heuristic fallback into one explicit server-owned policy layer:

- role-sensitive guided registration/build paths now share a deterministic
  naming-policy module
- weak abbreviations can return actionable warnings with semantic suggestions
- clearly opaque placeholder names can be blocked before guided execution
  proceeds
- prompts, MCP docs, runtime behavior, and regression coverage now tell the
  same naming-policy story

## What Changed

- added:
  - `server/adapters/mcp/guided_naming_policy.py`
  - `server/adapters/mcp/contracts/guided_naming.py`
  with one shared decision model for:
  - `allowed`
  - `warning`
  - `blocked`
  including reason codes, suggested names, and canonical naming patterns
- extended router-facing contracts in:
  - `server/adapters/mcp/contracts/router.py`
  so `guided_register_part(...)` can return structured `guided_naming`
  diagnostics
- added explicit rollout config in:
  - `server/infrastructure/config.py`
  with `MCP_GUIDED_NAMING_POLICY_MODE`
- integrated naming-policy checks into:
  - `server/adapters/mcp/router_helper.py`
  for role-sensitive build calls carrying `guided_role=...`
  - `server/adapters/mcp/areas/router.py`
  for the canonical `guided_register_part(...)` path
- kept existing seam heuristics in:
  - `server/application/services/spatial_graph.py`
  - `server/adapters/mcp/areas/reference.py`
  as recovery/backstop logic instead of turning them into the primary naming
  policy
- updated prompt/operator docs in:
  - `README.md`
  - `_docs/_MCP_SERVER/README.md`
  - `_docs/_PROMPTS/GUIDED_SESSION_START.md`
  - `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
  - `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
  - `_docs/_PROMPTS/README.md`
  so they now explain preferred semantic names, warning behavior, blocked
  placeholder names, and the canonical/convenience role-registration paths
- added/updated regressions across:
  - `tests/unit/adapters/mcp/test_guided_naming_policy.py`
  - `tests/unit/adapters/mcp/test_router_elicitation.py`
  - `tests/unit/adapters/mcp/test_context_bridge.py`
  - `tests/unit/adapters/mcp/test_search_surface.py`
  - `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
  - `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
  - `tests/unit/adapters/mcp/test_public_surface_docs.py`
  - `tests/unit/adapters/mcp/test_reference_images.py`
  - `tests/unit/tools/test_handler_rpc_alignment.py`
  - `tests/e2e/integration/test_guided_surface_contract_parity.py`
  - `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Why

Before this change the project had:

- good prompt guidance about semantic names
- good role/family enforcement
- heuristic recovery for some weak names

but no deterministic server policy deciding when a role-sensitive object name
was acceptable, weak, or too opaque. That left naming quality partly in prompt
compliance and partly in heuristic recovery. The new policy layer closes that
gap without replacing the existing seam heuristics.

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_naming_policy.py tests/unit/adapters/mcp/test_router_elicitation.py tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_search_surface.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_naming_policy.py tests/unit/adapters/mcp/test_router_elicitation.py tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/adapters/mcp/test_reference_images.py -q -k 'not slow'`
- `PYTHONPATH=. poetry run pytest tests/unit/tools/test_handler_rpc_alignment.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py tests/e2e/integration/test_guided_streamable_spatial_support.py -q`
  - result on this machine: `1 passed, 2 skipped`
  - the skips were transport-backed scenarios gated by the local runtime/test environment
