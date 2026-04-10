# TASK-152-02: Inspect Validate Surface And Attachment Family Alignment

**Parent:** [TASK-152](./TASK-152_Guided_Spatial_Gate_Usability_Prompt_Semantics_And_Inspect_Alignment.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Remove the contradiction between:

- `guided_flow_state.allowed_families`
- inspect-visible tool exposure
- the actual availability of attachment macros during `inspect_validate`

## Repository Touchpoints

- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/router_helper.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Acceptance Criteria

- the inspect surface and the guided flow contract agree on whether
  `attachment_alignment` work is still available in `inspect_validate`
- blocked/exposed guidance in runtime matches the docs/prompts

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-152-02-01](./TASK-152-02-01_Decide_Inspect_Validate_Attachment_Policy.md) | Choose the canonical policy for attachment macros in `inspect_validate` |
| 2 | [TASK-152-02-02](./TASK-152-02-02_Align_Visibility_Allowed_Families_And_Blocked_Guidance.md) | Implement the chosen policy across visibility, flow state, and blocked guidance |

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Changelog Impact

- include in the parent TASK-152 changelog entry
