# TASK-140-04-02: Selected NVIDIA Family Routing and Compare Path

**Parent:** [TASK-140-04](./TASK-140-04_NVIDIA_VLM_Support_And_Exclusion_Policy.md)
**Depends On:** [TASK-140-04-01](./TASK-140-04-01_NVIDIA_VLM_Family_Triage_Compare_Vs_Document_And_Retrieval.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Implement the runtime/config/backend routing for the NVIDIA compare-capable
subset on the existing external runtime path only, without broadening support
to unrelated NVIDIA visual model classes.

## Repository Touchpoints

- `server/infrastructure/config.py`
- `server/adapters/mcp/vision/config.py`
- `server/adapters/mcp/vision/runtime.py`
- `server/adapters/mcp/vision/backends.py`
- `server/adapters/mcp/sampling/result_types.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/unit/adapters/mcp/test_vision_result_types.py`
- `.env.example`

## Acceptance Criteria

- the selected NVIDIA compare subset has one explicit family/profile routing
  story on the current external runtime path
- request assumptions are validated for that path
- runtime selection does not imply support for excluded NVIDIA visual families
- unknown or non-matching NVIDIA-family ids still fall back to `generic_full`
- this slice does not assume a new NVIDIA-specific provider branch unless the
  current external transport path is proven insufficient
- any newly introduced NVIDIA-specific `vision_contract_profile` values remain
  typed in public `VisionAssistContract` result surfaces

## Docs To Update

- `.env.example`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/unit/adapters/mcp/test_vision_result_types.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped
