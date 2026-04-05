# TASK-139-03-02: OpenRouter Google-Family Repair and Failure Surface

**Parent:** [TASK-139-03](./TASK-139-03_Parser_Repair_And_Diagnostics_By_Contract_Profile.md)
**Depends On:** [TASK-139-03-01](./TASK-139-03-01_Profile_Aware_Parse_And_Diagnose_Flow.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Reuse or extend the narrow compare repair path for OpenRouter-hosted
Google-family models and improve the failure surface so operators can tell
whether a staged-loop failure was caused by transport, contract, or model
behavior.

## Business Problem

Current operator experience is too binary:

- prose is correctly rejected
- but the failure surface does not yet clearly explain that the model may have
  been run under a mismatched vision contract profile

That slows down diagnosis and makes provider/model notes harder to trust.

## Repository Touchpoints

- `server/adapters/mcp/vision/parsing.py`
- `server/adapters/mcp/vision/backends.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- OpenRouter Google-family compare flows can reuse near-JSON/truncated-JSON
  repair where the selected `vision_contract_profile` allows it
- the failure surface keeps hard rejection of prose/no-JSON responses
- diagnostics and error text make the selected `vision_contract_profile`
  visible enough for operators and tests

## Leaf Work Items

- extend the compare-flow repair path beyond the `google_ai_studio` transport
  gate
- add regression coverage for OpenRouter + Google-family malformed/near-JSON
  outputs
- tighten operator-facing error text and provider-note wording around
  vision-contract-profile mismatch versus model instability

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`

## Docs To Update

- `_docs/_VISION/README.md`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped

## Status / Board Update

- keep board tracking on the parent parser/diagnostics slice unless this leaf
  is promoted independently
- when this leaf closes, update the parent task summary so the OpenRouter
  Google-family repair path and tightened failure-surface wording are recorded
  explicitly
