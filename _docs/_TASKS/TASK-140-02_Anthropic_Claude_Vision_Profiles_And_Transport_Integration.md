# TASK-140-02: Anthropic Claude Vision Profiles and Transport Integration

**Parent:** [TASK-140](./TASK-140_Expand_External_Vision_Contract_Profiles_Across_Qwen_Anthropic_OpenAI_And_NVIDIA.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Add one intentional Anthropic / Claude external vision path with explicit
provider/config typing, request assembly, and parser/diagnostic policy instead
of forcing Claude support through an unrelated OpenAI-compatible assumption.

## Business Problem

Claude image-input support matters for this umbrella, but the current runtime
does not have a first-class Anthropic transport/provider branch. Treating
Claude as "just another generic external provider" would blur transport,
prompting, and parse-repair responsibilities again.

## Repository Touchpoints

- `server/infrastructure/config.py`
- `server/adapters/mcp/vision/config.py`
- `server/adapters/mcp/vision/runtime.py`
- `server/adapters/mcp/vision/backends.py`
- `server/adapters/mcp/vision/parsing.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Acceptance Criteria

- Anthropic has an explicit provider/config/runtime path
- Claude image-input request assembly is transport-correct
- the repo records whether Claude families share one compare profile or need
  stricter separation
- Anthropic failures can be diagnosed without pretending they are
  OpenAI-compatible transport failures

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`

## Changelog Impact

- include in the parent umbrella changelog entry when shipped

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-140-02-01](./TASK-140-02-01_Anthropic_Typed_Config_And_Provider_Surface.md) | Add typed Anthropic config/runtime/provider vocabulary |
| 2 | [TASK-140-02-02](./TASK-140-02-02_Anthropic_Request_Assembly_And_Image_Payload_Contract.md) | Implement Anthropic message/image payload assembly without reusing incompatible transport logic |
| 3 | [TASK-140-02-03](./TASK-140-02-03_Anthropic_Parse_Diagnostics_And_Compare_Profile_Policy.md) | Define Claude compare-profile behavior plus Anthropic-specific diagnostics and repair policy |
