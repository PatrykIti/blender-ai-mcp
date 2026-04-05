# TASK-139-01-01: Contract Profile Vocabulary and Typed Config Surface

**Parent:** [TASK-139-01](./TASK-139-01_Runtime_Contract_Profile_Model_And_Resolution.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Define the explicit vocabulary for external vision contract profiles and add the
typed config/runtime fields needed to carry that selection through the stack.

## Technical Direction

First-pass profile vocabulary should separate at least:

- a generic full external contract
- a narrow compare contract for Google-family staged compare flows
- room for future model-family-specific profiles without reworking the typing
  again

The contract-profile field should be explicit in typed config/runtime models,
not only inferred transiently in helper functions.

## Repository Touchpoints

- `server/adapters/mcp/vision/config.py`
- `server/adapters/mcp/vision/runtime.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`

## Acceptance Criteria

- one stable profile vocabulary exists in typed config
- runtime config carries the resolved active contract profile
- the typed surface is explicit enough that downstream code can use the profile
  directly instead of re-deriving it ad hoc

## Leaf Work Items

- add the contract-profile field(s) to external vision config/runtime models
- decide whether the explicit override should live in config, resolved runtime
  state, or both
- expose the resolved profile in diagnostics-friendly runtime state

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped
