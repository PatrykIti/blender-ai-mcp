# TASK-140-02-02: Anthropic Request Policy on the Existing External Path

**Parent:** [TASK-140-02](./TASK-140-02_Anthropic_Claude_Vision_Profiles_And_Transport_Integration.md)
**Depends On:** [TASK-140-02-01](./TASK-140-02-01_Anthropic_Typed_Config_And_Provider_Surface.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Determine whether Claude-family compare flows on the existing external runtime
path can reuse the current request assembly, or whether they need bounded
contract-aware request adjustments without turning this wave into a new
provider integration.

## Repository Touchpoints

- `server/adapters/mcp/vision/backends.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Acceptance Criteria

- Claude-family requests are validated against the assumptions of the current
  external runtime path
- bounded system/prompt/schema behavior still flows through
  `vision_contract_profile`
- any request-shape differences stay bounded to family/contract needs and do
  not redefine profile-selection policy owned by runtime/prompting layers
- if the current external transport path cannot support the required behavior,
  the task records that gap explicitly instead of silently adding a new
  provider branch

## Docs To Update

- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_external_backend.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped
