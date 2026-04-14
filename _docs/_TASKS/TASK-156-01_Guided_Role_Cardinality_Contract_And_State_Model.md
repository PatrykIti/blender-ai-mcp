# TASK-156-01: Guided Role Cardinality Contract And State Model

**Parent:** [TASK-156](./TASK-156_Guided_Pair_Role_Cardinality_And_Sibling_Part_Registration.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Add explicit cardinality metadata to guided role definitions and session
summaries.

## Repository Touchpoints

- `server/adapters/mcp/contracts/guided_flow.py`
- `server/adapters/mcp/session_capabilities.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- guided role definitions can declare required object count
- public role summaries remain compact but expose enough information to avoid
  singleton/pair ambiguity
- existing singleton role behavior remains unchanged

## Tests To Add/Update

- Unit coverage for singleton and pair cardinality summary generation

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Changelog Impact

- include in the TASK-156 changelog entry

## Status / Closeout Note

- when this leaf closes, record the public role-summary shape and any backward
  compatibility notes for existing `allowed_roles` / `completed_roles` fields

## Completion Summary

- added role cardinality summary fields to `GuidedFlowStateContract`: `role_counts`, `role_cardinality`, and `role_objects`
- added pair cardinality metadata for creature pair roles while preserving singleton behavior for existing roles
