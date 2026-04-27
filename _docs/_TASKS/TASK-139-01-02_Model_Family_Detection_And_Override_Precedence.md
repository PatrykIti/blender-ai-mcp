# TASK-139-01-02: Vision Contract Profile Model-Family Detection and Override Precedence

**Parent:** [TASK-139-01](./TASK-139-01_Runtime_Contract_Profile_Model_And_Resolution.md)
**Depends On:** [TASK-139-01-01](./TASK-139-01-01_Contract_Profile_Vocabulary_And_Typed_Config_Surface.md)
**Status:** ✅ Done
**Priority:** 🔴 High

**Completion Summary:** Runtime resolution now applies one explicit precedence
order: `VISION_EXTERNAL_CONTRACT_PROFILE` override first, Google-family
model-id auto-match second, provider default third, and `generic_full`
fallback last.

## Objective

Define deterministic precedence rules so vision-contract-profile selection can
be driven by an explicit flat config/env override first, then model-family
matching, then provider default behavior.

## Business Problem

Without explicit precedence rules, the repo will drift into unpredictable
vision-contract-profile selection:

- provider identity may override model behavior when it should not
- model-name heuristics may override explicit operator intent when they should
  not
- docs/tests may not agree on why one profile was selected

## Repository Touchpoints

- `server/infrastructure/config.py`
- `server/adapters/mcp/vision/runtime.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Acceptance Criteria

- precedence is explicit and documented:
  - explicit `VISION_EXTERNAL_CONTRACT_PROFILE` override
  - model-family match
  - provider-default vision contract profile
- the explicit override path is defined at the `Config` layer and documented
  clearly enough that tests/docs agree on why a profile was selected
- Google-family models behind OpenRouter can be matched into the narrow compare
  contract when desired
- conflicting provider/model combinations do not produce ambiguous
  `vision_contract_profile` selection

## Leaf Work Items

- define first-pass Google-family model matching rules for OpenRouter-hosted
  model ids
- define the explicit override path on the flat config/env surface using
  `VISION_EXTERNAL_CONTRACT_PROFILE` and document when it must suppress
  automatic model-family routing
- add regression cases for explicit override, auto-match, and fallback behavior

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped

## Status / Board Update

- keep board tracking on the parent runtime slice unless this leaf is promoted
  independently
- when this leaf closes, update the parent task summary so the precedence order
  and override behavior are called out explicitly
