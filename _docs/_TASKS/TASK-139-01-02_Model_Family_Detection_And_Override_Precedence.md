# TASK-139-01-02: Model Family Detection and Override Precedence

**Parent:** [TASK-139-01](./TASK-139-01_Runtime_Contract_Profile_Model_And_Resolution.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Define deterministic precedence rules so contract-profile selection can be
driven by explicit override first, then model-family matching, then provider
default behavior.

## Business Problem

Without explicit precedence rules, the repo will drift into unpredictable
profile selection:

- provider identity may override model behavior when it should not
- model-name heuristics may override explicit operator intent when they should
  not
- docs/tests may not agree on why one profile was selected

## Repository Touchpoints

- `server/adapters/mcp/vision/runtime.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- precedence is explicit and documented:
  - explicit override
  - model-family match
  - provider default
- Google-family models behind OpenRouter can be matched into the narrow compare
  contract when desired
- conflicting provider/model combinations do not produce ambiguous profile
  selection

## Leaf Work Items

- define first-pass Google-family model matching rules for OpenRouter-hosted
  model ids
- document when explicit override must suppress automatic model-family routing
- add regression cases for explicit override, auto-match, and fallback behavior

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped
