# TASK-140-04-03: NVIDIA Non-Compare Exclusion Contracts and Diagnostics

**Parent:** [TASK-140-04](./TASK-140-04_NVIDIA_VLM_Support_And_Exclusion_Policy.md)
**Depends On:** [TASK-140-04-02](./TASK-140-04-02_Selected_NVIDIA_Provider_Surface_And_Compare_Path.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Make the NVIDIA exclusion boundary explicit in runtime behavior, diagnostics,
and docs so non-compare models do not appear "partially supported" by accident.

## Repository Touchpoints

- `server/adapters/mcp/vision/runtime.py`
- `server/adapters/mcp/vision/parsing.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- excluded NVIDIA visual families have explicit runtime or docs-visible
  exclusion semantics
- diagnostics make it clear when a model is outside the compare-support matrix
- diagnostics preserve the `TASK-139` fallback story by making it clear when a
  non-matching NVIDIA-family id stayed on `generic_full`
- the repo does not conflate document/retrieval capability with compare
  capability

## Docs To Update

- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped
