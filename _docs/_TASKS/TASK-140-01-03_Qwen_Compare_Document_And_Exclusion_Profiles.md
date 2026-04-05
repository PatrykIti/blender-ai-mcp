# TASK-140-01-03: Qwen Compare, Document, and Exclusion Profiles

**Parent:** [TASK-140-01](./TASK-140-01_Qwen_Family_Contract_Profile_Matrix_And_Routing.md)
**Depends On:** [TASK-140-01-02](./TASK-140-01-02_Qwen_Runtime_Profile_Vocabulary_And_Model_ID_Routing.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Define the concrete prompt/schema/request/parser behavior for the Qwen
profiles chosen by the runtime and keep document/OCR-oriented variants from
silently inheriting compare contracts they should not use.

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
