# TASK-152-02-01: Decide Inspect Validate Attachment Policy

**Parent:** [TASK-152-02](./TASK-152-02_Inspect_Validate_Surface_And_Attachment_Family_Alignment.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Choose one canonical product policy for attachment repair in
`inspect_validate`.

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`

## Decision To Make

Choose one of:

1. keep `attachment_alignment` allowed in `inspect_validate` and expose the
   relevant macros there
2. remove `attachment_alignment` from `inspect_validate` and make the blocked
   guidance explicit that attachment repair requires stepping back into an
   earlier guided family/state

## Acceptance Criteria

- one canonical inspect policy is documented and no longer contradicted by
  runtime behavior

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`

## Changelog Impact

- include in the parent TASK-152 changelog entry
