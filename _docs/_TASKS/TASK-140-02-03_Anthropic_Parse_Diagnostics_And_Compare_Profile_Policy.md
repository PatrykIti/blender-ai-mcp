# TASK-140-02-03: Anthropic Parse, Diagnostics, and Compare-Profile Policy

**Parent:** [TASK-140-02](./TASK-140-02_Anthropic_Claude_Family_Contracts_On_The_Existing_Provider_Surface.md)
**Depends On:** [TASK-140-02-02](./TASK-140-02-02_Anthropic_Request_Assembly_And_Image_Payload_Contract.md)
**Status:** ⏭️ Superseded
**Priority:** 🔴 High
**Superseded By:** [TASK-187](./TASK-187_External_Vision_Model_Evidence_And_Profile_Promotion_Governance.md)
**Superseded Reason:** Replaced by the capability-first OpenRouter metadata, fallback capability registry, and request-policy model. Family-specific profiles return under `TASK-187` only when harness/operator evidence shows a real contract delta.

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

## Implementation Notes

- keep this leaf focused on parser/diagnostic behavior and explicit
  compare-profile policy once routing and request-shape work are known
- make Claude-family diagnostics explain:
  - chosen profile
  - fallback path
  - contract mismatch versus plain model failure
- keep result-contract typing aligned when a Claude-specific profile becomes
  visible to operators

## Runtime / Security Contract Notes

- parser/repair policy must stay strict enough that prose reasoning is not
  mistaken for contract success
- diagnostics should surface bounded failure reasons without leaking raw
  provider payloads or secrets

## Docs To Update

- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/unit/adapters/mcp/test_vision_result_types.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_vision_parsing.py tests/unit/adapters/mcp/test_vision_external_backend.py tests/unit/adapters/mcp/test_vision_result_types.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Status / Board Update

- remains nested under `TASK-140-02`
- should close only after routing and request-assembly decisions are reflected
  in parser/diagnostic behavior
