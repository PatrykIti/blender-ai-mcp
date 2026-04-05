# TASK-139-01-01: Vision Contract Profile Vocabulary and Typed Config Surface

**Parent:** [TASK-139-01](./TASK-139-01_Runtime_Contract_Profile_Model_And_Resolution.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Define the explicit vocabulary for external vision contract profiles and add the
typed config/runtime fields needed to carry that selection through the stack.

## Technical Direction

First-pass `VisionContractProfile` vocabulary should separate at least:

- a generic full external contract
- a narrow compare contract for Google-family staged compare flows
- room for future model-family-specific profiles without reworking the typing
  again

The `vision_contract_profile` field should be explicit in typed config/runtime
models, not only inferred transiently in helper functions. The flat
application config surface that feeds runtime resolution also needs a
first-class `VISION_EXTERNAL_CONTRACT_PROFILE` override instead of relying only
on downstream typed models.

## Repository Touchpoints

- `server/infrastructure/config.py`
- `server/adapters/mcp/vision/config.py`
- `server/adapters/mcp/vision/runtime.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Acceptance Criteria

- one stable vision-contract-profile vocabulary exists in the flat config/env
  surface and in typed runtime config
- runtime config carries the resolved active `vision_contract_profile`
- the typed surface is explicit enough that downstream code can use the
  `vision_contract_profile` directly instead of re-deriving it ad hoc

## Leaf Work Items

- add the `VISION_EXTERNAL_CONTRACT_PROFILE` env/config field and the
  `vision_contract_profile` typed field(s) to external vision config/runtime
  models
- decide what the explicit override looks like at the `Config` layer and how it
  maps into resolved `vision_contract_profile` runtime state
- expose the resolved `vision_contract_profile` in diagnostics-friendly runtime
  state

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
- when this leaf closes, update the parent task summary so the config/runtime
  vocabulary decision is recorded explicitly
