# TASK-140-02: Anthropic Claude Family Contracts on the Existing External Path

**Parent:** [TASK-140](./TASK-140_Expand_External_Vision_Contract_Profiles_Across_Qwen_Anthropic_OpenAI_And_NVIDIA.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Define one intentional Anthropic / Claude model-family contract story for the
external vision runtime, centered on the existing external transport path,
instead of forcing Claude-family ids through one generic profile.

## Business Problem

Claude image-input support matters for this umbrella, but `TASK-140` is not
primarily about adding a first-class Anthropic provider branch. The real
question is whether Claude-family ids routed through the current external path
need family-specific contracts beyond `generic_full`.

Treating Claude as "just another generic external model" would blur family
routing, prompting, and parse-repair responsibilities again.

## Repository Touchpoints

- `server/infrastructure/config.py`
- `server/adapters/mcp/vision/config.py`
- `server/adapters/mcp/vision/runtime.py`
- `server/adapters/mcp/vision/prompting.py`
- `server/adapters/mcp/vision/backends.py`
- `server/adapters/mcp/vision/parsing.py`
- `server/adapters/mcp/sampling/result_types.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_result_types.py`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Acceptance Criteria

- Claude-family model-id routing is explicit on the current external runtime
  path
- Claude request/prompt/parser behavior is deliberate instead of inherited by
  accident from `generic_full`
- the repo records whether Claude families share one compare profile or need
  stricter separation
- if the current external transport path is insufficient for Claude-family
  behavior, the gap is recorded explicitly as a bounded follow-on instead of
  silently broadening provider scope
- if Claude-specific `vision_contract_profile` values are introduced, they
  remain typed in public `VisionAssistContract` result surfaces
- unknown or non-matching Claude-family ids still fall back to `generic_full`
  under the `TASK-139` precedence model
- Anthropic failures can be diagnosed without pretending they are
  generic external contract failures

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_result_types.py`

## Changelog Impact

- include in the parent umbrella changelog entry when shipped

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-140-02-01](./TASK-140-02-01_Anthropic_Typed_Config_And_Provider_Surface.md) | Add Claude-family routing and typed contract vocabulary on the existing external runtime path |
| 2 | [TASK-140-02-02](./TASK-140-02-02_Anthropic_Request_Assembly_And_Image_Payload_Contract.md) | Decide whether existing external request assembly is sufficient for Claude-family ids or needs bounded contract-aware adjustments |
| 3 | [TASK-140-02-03](./TASK-140-02-03_Anthropic_Parse_Diagnostics_And_Compare_Profile_Policy.md) | Define Claude compare-profile behavior plus contract-aware diagnostics and repair policy |
