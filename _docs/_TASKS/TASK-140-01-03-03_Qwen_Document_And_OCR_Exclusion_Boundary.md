# TASK-140-01-03-03: Qwen Document and OCR Exclusion Boundary

**Parent:** [TASK-140-01-03](./TASK-140-01-03_Qwen_Compare_Document_And_Exclusion_Profiles.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Draw the hard product boundary for Qwen document/OCR-oriented variants so the
repo does not silently route them into staged compare flows unless that is a
deliberate, tested decision.

## Repository Touchpoints

- `server/adapters/mcp/vision/runtime.py`
- `server/adapters/mcp/vision/prompting.py`
- `server/adapters/mcp/vision/parsing.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- document/OCR-oriented Qwen families have one explicit compare policy:
  separate document profile, compare exclusion, or later follow-on
- diagnostics and docs make that exclusion visible enough that operators do
  not mistake document models for supported compare models
- runtime selection does not silently auto-match document models into a
  compare-capable profile

## Docs To Update

- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped
