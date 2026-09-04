# TASK-154-01: Naming Policy Contract And Role-Based Suggestion Vocabulary

**Parent:** [TASK-154](./TASK-154_Guided_Naming_Policy_And_Semantic_Object_Name_Enforcement.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Define the deterministic policy contract for guided object naming and the
canonical role/domain-specific suggestion vocabulary it will use.

## Repository Touchpoints

- `server/adapters/mcp/guided_naming_policy.py`
- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/areas/modeling.py`
- `server/adapters/mcp/session_capabilities.py`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- the task defines:
  - where naming policy runs
  - which inputs it needs
  - what result envelope it returns
  - what canonical suggestions exist per role/domain
- the policy contract is precise enough that runtime integration leaves can be
  implemented without rediscovering semantics ad hoc

## Detailed Implementation Notes

- this subtask should freeze the contract before runtime wiring begins
- it should explicitly separate:
  - semantic object naming policy
  - public tool/argument naming transforms
  - heuristic seam recovery
- it should decide whether the policy result includes:
  - severity/status
  - message
  - suggested names
  - canonical naming pattern
  - machine-readable reason code

## Planned Validation Matrix

- design completeness:
  - every integration hook has enough context to call the policy
  - every role/domain used in guided execution has at least one canonical name
    suggestion
- docs parity:
  - prompt docs and MCP docs describe the same preferred naming story before
    runtime enforcement lands

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-154-01-01](./TASK-154-01-01_Audit_Current_Naming_Drift_And_Runtime_Hook_Points.md) | Audit current prompt/runtime/heuristic naming behavior and identify the deterministic hook points |
| 2 | [TASK-154-01-02](./TASK-154-01-02_Define_Guided_Naming_Policy_Result_Contract_And_Suggestion_Map.md) | Define the shared result contract and the role-based semantic naming suggestions |

## Docs To Update

- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- design/docs parity tests land in the parent closeout wave
- `tests/unit/adapters/mcp/test_guided_naming_policy.py`
  should land once the result contract is implemented

## Changelog Impact

- include in the parent TASK-154 changelog entry

## Completion Summary

- froze the naming-policy contract, role/domain vocabulary, reason codes, and
  suggestion map before runtime wiring landed
