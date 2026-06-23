# TASK-140-02-02: Anthropic Request Policy on the Existing Shared Backend Path

**Parent:** [TASK-140-02](./TASK-140-02_Anthropic_Claude_Family_Contracts_On_The_Existing_Provider_Surface.md)
**Depends On:** [TASK-140-02-01](./TASK-140-02-01_Anthropic_Family_Routing_And_Typed_Contract_Vocabulary.md)
**Status:** ⏭️ Superseded
**Priority:** 🔴 High
**Superseded By:** [TASK-187](./TASK-187_External_Vision_Model_Evidence_And_Profile_Promotion_Governance.md)
**Superseded Reason:** Replaced by the capability-first OpenRouter metadata, fallback capability registry, and request-policy model. Family-specific profiles return under `TASK-187` only when harness/operator evidence shows a real contract delta.

## Objective

Determine whether Claude-family compare flows on the current shared
`openai_compatible_external` backend path can reuse the current request
assembly, or whether they need bounded contract-aware request adjustments
without turning this wave into provider integration or a new transport branch.

## Backend Constraint

This leaf works inside the backend seam already present in
`server/adapters/mcp/vision/backends.py`.

- `google_ai_studio` remains the only dedicated transport/request branch
- OpenRouter-like families stay on the shared chat-completions path with
  provider headers / strict-schema formatting where already supported
- Claude-family work may only add bounded contract-aware request behavior
  within that shared path

## Repository Touchpoints

- `server/adapters/mcp/vision/backends.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Acceptance Criteria

- Claude-family requests are validated against the assumptions of the current
  shared external backend path
- bounded system/prompt/schema behavior still flows through
  `vision_contract_profile`
- any request-shape differences stay bounded to family/contract needs and do
  not redefine profile-selection policy owned by runtime/prompting layers
- if the current shared backend seam cannot support the required behavior, the
  task records that gap explicitly instead of silently adding a new provider
  branch or transport path

## Implementation Notes

- keep this leaf on `vision/backends.py` and the current shared request seam
  only
- validate whether Claude-family ids need bounded request-shape adjustments
  without changing who owns family selection or profile vocabulary
- coordinate the result with the routing leaf and the later parse/diagnostic
  leaf so request behavior does not drift from documented contract choices

## Runtime / Security Contract Notes

- do not add a dedicated Anthropic transport branch
- if request differences are required, keep them explicitly profile-aware and
  bounded to the shared backend path

## Docs To Update

- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_external_backend.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_external_backend.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Status / Board Update

- remains nested under `TASK-140-02`
- should close before parse/diagnostic policy is finalized for Claude-family
  ids
