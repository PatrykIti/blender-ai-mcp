# TASK-140-02-02: Anthropic Request Assembly and Image Payload Contract

**Parent:** [TASK-140-02](./TASK-140-02_Anthropic_Claude_Vision_Profiles_And_Transport_Integration.md)
**Depends On:** [TASK-140-02-01](./TASK-140-02-01_Anthropic_Typed_Config_And_Provider_Surface.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Implement Anthropic request assembly for bounded compare flows using
Anthropic-correct message and image payload semantics rather than forcing the
OpenAI-compatible transport path to impersonate Claude.

## Repository Touchpoints

- `server/adapters/mcp/vision/backends.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Acceptance Criteria

- Anthropic requests are transport-correct for image input
- bounded system/prompt/schema behavior still flows through
  `vision_contract_profile`
- Anthropic integration does not redefine profile-selection policy that should
  remain owned by runtime/prompting layers

## Docs To Update

- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_external_backend.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped
