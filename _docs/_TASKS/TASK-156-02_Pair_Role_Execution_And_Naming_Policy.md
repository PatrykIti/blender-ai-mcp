# TASK-156-02: Pair Role Execution And Naming Policy

**Parent:** [TASK-156](./TASK-156_Guided_Pair_Role_Cardinality_And_Sibling_Part_Registration.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Make guided execution and naming policy honor pair-role cardinality for ears
and legs.

## Repository Touchpoints

- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/guided_naming_policy.py`
- `server/adapters/mcp/areas/modeling.py`
- `server/adapters/mcp/areas/router.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/unit/adapters/mcp/test_guided_naming_policy.py`

## Acceptance Criteria

- second sibling object under the same pair role is allowed
- third object under the same pair role is blocked with actionable guidance
- naming warnings suggest the missing side-specific sibling when possible

## Tests To Add/Update

- Unit coverage for `ear_pair`, `foreleg_pair`, and `hindleg_pair`
- E2E guided creature transport coverage for side-pair creation

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`

## Changelog Impact

- include in the TASK-156 changelog entry

## Status / Closeout Note

- when this leaf closes, record the role cardinality policy, side-specific
  naming suggestions, and the exact block message for over-cardinality calls

## Completion Summary

- role completion now depends on cardinality, so one side-specific pair object no longer completes the whole pair role
- execution policy continues to allow the second sibling and blocks a third sibling once the pair is complete
