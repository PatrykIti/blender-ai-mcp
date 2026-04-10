# TASK-154: Guided Naming Policy And Semantic Object Name Enforcement

**Status:** ✅ Done
**Priority:** 🔴 High
**Category:** Guided Runtime / LLM UX / Naming Policy
**Estimated Effort:** Large
**Follow-on After:** [TASK-152](./TASK-152_Guided_Spatial_Gate_Usability_Prompt_Semantics_And_Inspect_Alignment.md)

## Objective

Introduce a server-owned guided naming policy so `llm-guided` can move beyond
prompt-only naming guidance and heuristic fallback toward deterministic,
role-aware naming advice and enforcement for object creation/registration.

## Business Problem

Today the repo already does three separate things:

1. prompt/docs guidance prefers full semantic names such as `Body`,
   `Head`, `ForeLeg_L`, and `HindLeg_R`
2. guided execution enforces semantic **roles** through
   `guided_register_part(...)` / `guided_role=...`
3. scene/reference heuristics try to recover meaning from weaker names such as
   `ForeL` / `HindR`

That still leaves one architectural gap:

- the model can keep generating opaque or inconsistent object names
- the runtime can still understand some of them heuristically
- but there is no deterministic policy layer that says:
  - whether the name is acceptable for the current role/step
  - what better name the model should use
  - whether the server should warn or block

This keeps naming quality partly inside prompt compliance and partly inside
heuristic recovery, instead of making it an explicit guided-loop policy.

## Current Code Baseline

- prompt guidance:
  - `_docs/_PROMPTS/GUIDED_SESSION_START.md`
  - `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
  - `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
  - `server/adapters/mcp/surfaces.py`
- semantic role enforcement:
  - `server/adapters/mcp/router_helper.py`
  - `server/adapters/mcp/areas/router.py`
  - `server/adapters/mcp/areas/modeling.py`
  - `server/adapters/mcp/session_capabilities.py`
- heuristic fallback:
  - `server/application/services/spatial_graph.py`
  - `server/adapters/mcp/areas/reference.py`

## Acceptance Criteria

- the guided runtime has one explicit naming-policy layer for role-sensitive
  object creation/registration
- the policy can return actionable guidance, not just silent heuristic fallback
- prompt/docs guidance, blocked/warning messages, and runtime behavior all say
  the same thing about preferred semantic names
- tests cover advisory and enforcement behavior across unit and transport paths

## Planned File Change Map

- `server/adapters/mcp/guided_naming_policy.py`
  - add the shared policy module, result contract, and role/domain suggestion
    vocabulary
- `server/adapters/mcp/router_helper.py`
  - integrate naming-policy checks into guided execution blocking/allow paths
- `server/adapters/mcp/areas/router.py`
  - apply the policy on `guided_register_part(...)`
- `server/adapters/mcp/areas/modeling.py`
  - apply the policy on role-sensitive `guided_role=...` build calls
- `server/adapters/mcp/session_capabilities.py`
  - expose any small helpers needed to resolve valid roles/domain context for
    the policy layer
- `server/application/services/spatial_graph.py`
  - keep naming heuristics as recovery-only backstop logic
- `server/adapters/mcp/areas/reference.py`
  - keep reference-stage naming heuristics aligned as recovery-only backstop
- prompt/docs surfaces
  - explain preferred naming plus warning/block behavior consistently
- tests
  - cover pure policy evaluation, runtime integration, transport parity, docs
    parity, and heuristic backstop behavior

## Planned Validation Matrix

- unit / pure policy:
  - canonical semantic names are allowed
  - weak names produce warnings with deterministic suggestions
  - opaque role-sensitive names block in strict mode
- unit / runtime integration:
  - `guided_register_part(...)` and `guided_role=...` use the same policy
  - router/runtime blocked responses remain actionable and structured
  - `search_tools(...)` / `call_tool(...)` paths preserve the same behavior
- unit / heuristic backstop:
  - scene/reference seam heuristics still recover common abbreviated limb names
    when policy is advisory
- unit / docs parity:
  - prompts and MCP docs describe the same naming-policy contract
- E2E / transport:
  - stdio guided session warning path
  - stdio guided session blocked path
  - streamable guided session warning/block parity
  - search/list/call parity on the same session after naming-policy decisions

## Implementation Direction

1. Policy ownership
   - create one shared module such as
     `server/adapters/mcp/guided_naming_policy.py`
   - keep it in the guided runtime/policy layer, not in prompt assets and not
     in the public tool naming transform layer

2. Policy scope
   - evaluate naming only when the guided runtime has role/domain context
   - primary entry points:
     - `guided_register_part(...)`
     - build calls carrying `guided_role=...`
   - do not try to globally police every Blender object name in the repo

3. Policy behavior
   - support at least:
     - advisory/warning mode
     - bounded blocked mode for opaque role-sensitive names
   - always provide suggested better names derived from role + domain profile

4. Heuristic relationship
   - keep current seam/attachment heuristics as recovery/backstop logic
   - do not treat heuristic success as a substitute for naming policy quality

## Repository Touchpoints

- `server/adapters/mcp/guided_naming_policy.py`
- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/areas/modeling.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/application/services/spatial_graph.py`
- `server/adapters/mcp/areas/reference.py`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_MCP_SERVER/README.md`
- `README.md`
- `tests/unit/adapters/mcp/test_guided_naming_policy.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
- `_docs/_TASKS/README.md`

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_naming_policy.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when this task ships

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-154-01](./TASK-154-01_Naming_Policy_Contract_And_Role_Based_Suggestion_Vocabulary.md) | Define the naming-policy contract, hook points, and canonical role-based suggestion vocabulary |
| 2 | [TASK-154-02](./TASK-154-02_Runtime_Advisory_And_Enforcement_Integration_For_Guided_Naming.md) | Integrate advisory/enforcement behavior into guided registration and role-sensitive build calls |
| 3 | [TASK-154-03](./TASK-154-03_Regression_And_Docs_Closeout_For_Guided_Naming_Policy.md) | Lock the naming-policy architecture in with regressions, docs, and changelog closeout |

## Status / Board Update

- completed on 2026-04-10 and moved from the board-level follow-on queue into
  Done once runtime naming policy, regressions, docs, and changelog/history
  landed together

## Completion Summary

- added one shared guided naming-policy module and structured decision contract
- integrated naming checks into `guided_register_part(...)` and role-sensitive
  `guided_role=...` build paths
- preserved seam heuristics as recovery/backstop logic instead of using them as
  the primary naming policy
- aligned prompts, MCP docs, and transport/runtime behavior around semantic
  naming warnings/blocks
