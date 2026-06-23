# TASK-140-01-03-03: Qwen Document and OCR Exclusion Boundary

**Parent:** [TASK-140-01-03](./TASK-140-01-03_Qwen_Compare_Document_And_Exclusion_Profiles.md)
**Status:** ⏭️ Superseded
**Priority:** 🟠 High
**Superseded By:** [TASK-187](./TASK-187_External_Vision_Model_Evidence_And_Profile_Promotion_Governance.md)
**Superseded Reason:** Replaced by the capability-first OpenRouter metadata, fallback capability registry, and request-policy model. Family-specific profiles return under `TASK-187` only when harness/operator evidence shows a real contract delta.

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

## Implementation Notes

- use this leaf to make the Qwen document/OCR boundary explicit in runtime
  selection, docs, and diagnostics
- keep the outcome bounded to:
  - explicit exclusion
  - separate document profile
  - or an intentionally deferred follow-on
- coordinate the result with the shared Qwen behavior leaf so compare-capable
  families and excluded families do not overlap ambiguously

## Runtime / Security Contract Notes

- document/OCR families must never silently enter staged compare flows
- if a separate document profile is chosen later, keep it explicit and typed
  rather than piggybacking on compare defaults

## Docs To Update

- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_vision_external_backend.py -q`

## Status / Board Update

- remains nested under `TASK-140-01-03`
- should close before the parent Qwen behavior leaf is considered complete
