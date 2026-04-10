# TASK-154-02: Runtime Advisory And Enforcement Integration For Guided Naming

**Parent:** [TASK-154](./TASK-154_Guided_Naming_Policy_And_Semantic_Object_Name_Enforcement.md)
**Depends On:** [TASK-154-01](./TASK-154-01_Naming_Policy_Contract_And_Role_Based_Suggestion_Vocabulary.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Integrate the guided naming policy into the runtime so role-sensitive
registration/build paths can surface deterministic warnings or blocks.

## Repository Touchpoints

- `server/adapters/mcp/guided_naming_policy.py`
- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/areas/modeling.py`
- `server/adapters/mcp/session_capabilities.py`
- `tests/unit/adapters/mcp/test_guided_naming_policy.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Acceptance Criteria

- the runtime can emit actionable naming warnings/blocks on guided paths
- `guided_register_part(...)` and `guided_role=...` paths use the same naming
  policy
- policy modes are explicit and bounded

## Detailed Implementation Notes

- this subtask owns behavior, not just message wording
- the integration should preserve the current execution-enforcement model:
  - family/role checks still decide whether a tool is allowed by step
  - naming policy adds an orthogonal object-name quality decision
- expected precedence:
  1. missing role / wrong family blocks
  2. naming policy evaluates when role/domain context exists
  3. warning or blocked result is attached consistently across direct and
     proxied paths

## Planned File Change Map

- `server/adapters/mcp/guided_naming_policy.py`
  - implement the pure decision layer
- `server/adapters/mcp/router_helper.py`
  - attach naming-policy decisions to execution-policy results
- `server/adapters/mcp/areas/router.py`
  - enforce naming policy on `guided_register_part(...)`
- `server/adapters/mcp/areas/modeling.py`
  - enforce naming policy on `guided_role=...` create/transform calls
- `server/adapters/mcp/session_capabilities.py`
  - expose any small resolution helpers needed by the policy
- `tests/unit/adapters/mcp/test_guided_naming_policy.py`
  - pure policy unit cases
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
  - direct registration/build integration
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
  - creature vs building suggestion behavior
- `tests/unit/adapters/mcp/test_router_elicitation.py`
  - blocked/warning payload semantics on guided runtime decisions
- `tests/unit/adapters/mcp/test_search_surface.py`
  - call/search proxy behavior under warning/block policy
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
  - stdio same-session parity
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
  - streamable same-session parity

## Planned Validation Matrix

- unit / direct registration:
  - `guided_register_part(...)` returns deterministic warnings/blocks
- unit / build convenience path:
  - `guided_role=...` create/transform paths return the same naming decision
- unit / search/call parity:
  - `call_tool(...)` preserves blocked/warning naming semantics
  - search-first guidance remains coherent when a named tool later blocks on
    naming quality
- E2E / transport:
  - stdio and streamable sessions show the same warning/block behavior
  - the same session still keeps guided flow state coherent after a naming
    warning

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-154-02-01](./TASK-154-02-01_Shared_Guided_Naming_Policy_Module_And_Opaque_Name_Detection.md) | Implement the shared policy module and opaque-name detection logic |
| 2 | [TASK-154-02-02](./TASK-154-02-02_Integrate_Naming_Policy_Into_Guided_Register_Part_And_Build_Calls.md) | Run the policy on canonical registration and role-sensitive build calls |
| 3 | [TASK-154-02-03](./TASK-154-02-03_Actionable_Warnings_And_Policy_Modes_For_Guided_Naming.md) | Define warning/block modes and the exact user/model-facing guidance surface |

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_naming_policy.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Changelog Impact

- include in the parent TASK-154 changelog entry
