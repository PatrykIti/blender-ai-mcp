# TASK-140-02-01: Anthropic Typed Config and Provider Surface

**Parent:** [TASK-140-02](./TASK-140-02_Anthropic_Claude_Vision_Profiles_And_Transport_Integration.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Add the flat config/env surface and typed runtime models needed for Anthropic
vision support without overloading the existing OpenAI-compatible provider
surface.

## Repository Touchpoints

- `server/infrastructure/config.py`
- `server/adapters/mcp/vision/config.py`
- `server/adapters/mcp/vision/runtime.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `.env.example`

## Acceptance Criteria

- Anthropic provider/config vocabulary is explicit
- typed runtime config can expose Anthropic selection and any Anthropic-specific
  auth/base-url fields cleanly
- config precedence remains deterministic and compatible with `TASK-139`

## Docs To Update

- `.env.example`
- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped
