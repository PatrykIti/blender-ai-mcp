# TASK-140-02-03: Anthropic Parse, Diagnostics, and Compare-Profile Policy

**Parent:** [TASK-140-02](./TASK-140-02_Anthropic_Claude_Vision_Profiles_And_Transport_Integration.md)
**Depends On:** [TASK-140-02-02](./TASK-140-02-02_Anthropic_Request_Assembly_And_Image_Payload_Contract.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Define the Anthropic compare-profile policy and the parser/diagnostic behavior
needed to keep Claude failures explainable and bounded.

## Repository Touchpoints

- `server/adapters/mcp/vision/prompting.py`
- `server/adapters/mcp/vision/parsing.py`
- `server/adapters/mcp/sampling/result_types.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/unit/adapters/mcp/test_vision_result_types.py`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- Claude compare behavior has an explicit profile decision
- any newly introduced Claude-specific `vision_contract_profile` values are
  reflected in public `VisionAssistContract` typing and regression coverage
- Anthropic diagnostics surface contract/profile mismatches clearly enough for
  operator review and harness evidence
- diagnostics preserve the `TASK-139` fallback story by making it clear when a
  Claude-family id stayed on `generic_full` because no narrower family match
  was selected
- parser/repair policy does not silently accept prose just because Claude can
  reason well over images

## Docs To Update

- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/unit/adapters/mcp/test_vision_result_types.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped
