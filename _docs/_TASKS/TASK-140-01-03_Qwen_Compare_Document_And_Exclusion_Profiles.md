# TASK-140-01-03: Qwen Compare, Document, and Exclusion Profiles

**Parent:** [TASK-140-01](./TASK-140-01_Qwen_Family_Contract_Profile_Matrix_And_Routing.md)
**Depends On:** [TASK-140-01-02](./TASK-140-01-02_Qwen_Runtime_Profile_Vocabulary_And_Model_ID_Routing.md)
**Status:** ⏭️ Superseded
**Priority:** 🔴 High
**Superseded By:** [TASK-187](./TASK-187_External_Vision_Model_Evidence_And_Profile_Promotion_Governance.md)
**Superseded Reason:** Replaced by the capability-first OpenRouter metadata, fallback capability registry, and request-policy model. Family-specific profiles return under `TASK-187` only when harness/operator evidence shows a real contract delta.

## Objective

Define the concrete prompt/schema/request/parser behavior for the Qwen
profiles chosen by the runtime and keep document/OCR-oriented variants from
silently inheriting compare contracts they should not use.

This leaf is where the Qwen slice turns the `TASK-139` seam into actual
product behavior: deterministic family routing must end in explicit
compare/document/exclusion profile decisions instead of falling back by
accident to whatever generic prompt path happens to work.

## Backend Boundary

Qwen profile work stays inside the current shared external backend seam.

- backend changes stay on the current `openai_compatible_external` path
- `google_ai_studio` remains the only dedicated transport branch
- OpenRouter-hosted Qwen families stay on the shared backend path with
  profile-aware prompt/schema/request behavior, not a new Qwen-specific
  provider branch

## Repository Touchpoints

- `server/adapters/mcp/vision/prompting.py`
- `server/adapters/mcp/vision/backends.py`
- `server/adapters/mcp/vision/parsing.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- compare-capable Qwen families use an explicit compare profile rather than
  falling through to whichever generic prompt path happens to work
- document/OCR-oriented Qwen families do not silently reuse staged compare
  behavior unless that is an intentional product decision
- diagnostics and failure text remain explicit about the selected Qwen profile
- backend changes, if needed, stay bounded to shared-path request/schema
  behavior and do not add a Qwen-specific transport/provider branch
- the final Qwen behavior matrix is explicit across:
  - compare-capable families
  - document/OCR-oriented families
  - excluded or still-generic families
- families that are not yet explicitly classified still fall back to
  `generic_full` under the `TASK-139` precedence model

## Implementation Notes

- keep Qwen profile behavior on the current shared external backend seam and
  let the child leaves separate:
  - legacy Qwen-VL decisions
  - Qwen2.5/Qwen3 profile behavior
  - document/OCR exclusion semantics
- treat prompting, backend request shape, and parsing/diagnostics as one
  bounded contract decision instead of three drifting heuristics

## Runtime / Security Contract Notes

- do not add a Qwen-specific provider branch
- document/OCR-oriented Qwen models must fail or route explicitly instead of
  silently inheriting compare behavior
- keep any new profile names and exclusions visible in typed runtime behavior
  and docs

## Docs To Update

- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-140-01-03-01](./TASK-140-01-03-01_Legacy_Qwen_VL_Plus_And_Max_Profile_Decisions.md) | Decide how legacy `qwen-vl-plus` / `qwen-vl-max` map into compare-capable or generic profiles |
| 2 | [TASK-140-01-03-02](./TASK-140-01-03-02_Qwen2_5_VL_And_Qwen3_VL_Profile_Decisions.md) | Define compare-profile behavior for Qwen2.5-VL and Qwen3-VL lines without collapsing them into the legacy path |
| 3 | [TASK-140-01-03-03](./TASK-140-01-03-03_Qwen_Document_And_OCR_Exclusion_Boundary.md) | Decide which Qwen document/OCR-oriented variants get a separate profile or an explicit compare exclusion |

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_vision_parsing.py tests/unit/adapters/mcp/test_vision_external_backend.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Status / Board Update

- remains nested under `TASK-140-01`
- should close only after all three physical child leaves land with aligned
  runtime/docs evidence
