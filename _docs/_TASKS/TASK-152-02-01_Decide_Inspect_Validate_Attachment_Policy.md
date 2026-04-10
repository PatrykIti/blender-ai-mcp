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
- `tests/unit/adapters/mcp/test_visibility_policy.py`

## Decision To Make

Choose one of:

1. keep `attachment_alignment` allowed in `inspect_validate` and expose the
   relevant macros there
2. remove `attachment_alignment` from `inspect_validate` and make the blocked
   guidance explicit that attachment repair requires stepping back into an
   earlier guided family/state

## Decision Criteria

- if inspect is supposed to remain a truth-first review phase, prefer removing
  `attachment_alignment`
- if inspect is supposed to permit bounded final seating/fix macros, expose the
  exact attachment macro set there and test it explicitly

## Planned Unit Test Scenarios

- visibility policy for `inspect_validate` matches the chosen decision
- docs parity wording matches the chosen decision

## Acceptance Criteria

- one canonical inspect policy is documented and no longer contradicted by
  runtime behavior

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Changelog Impact

- include in the parent TASK-152 changelog entry
