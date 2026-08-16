# TASK-139-03-01: Vision-Contract-Profile-Aware Parse and Diagnose Flow

**Parent:** [TASK-139-03](./TASK-139-03_Parser_Repair_And_Diagnostics_By_Contract_Profile.md)
**Status:** ✅ Done
**Priority:** 🔴 High

**Completion Summary:** `parse_vision_output_text(...)` and
`diagnose_vision_output_text(...)` now take `vision_contract_profile` as a
first-class input while preserving the existing container/payload failure
classification surfaces.

## Objective

Thread the resolved `vision_contract_profile` through
`parse_vision_output_text(...)` and `diagnose_vision_output_text(...)` so
repair and classification can key off the selected vision contract profile
instead of provider identity alone.

## Repository Touchpoints

- `server/adapters/mcp/vision/parsing.py`
- `server/adapters/mcp/vision/backends.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`

## Acceptance Criteria

- parser/diagnostic entry points accept the selected `vision_contract_profile`
- provider-only repair branching is removed or reduced where
  vision-contract-profile branching is the real intent
- diagnostics still expose `container_shape` and `payload_shape` without
  losing the current failure classification

## Leaf Work Items

- add `vision_contract_profile` plumbing through the parser/diagnostic call
  chain
- keep backward compatibility for existing callers where possible
- expand unit coverage for vision-contract-profile-aware diagnostics

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_parsing.py`

## Docs To Update

- `_docs/_VISION/README.md`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped

## Status / Board Update

- keep board tracking on the parent parser/diagnostics slice unless this leaf
  is promoted independently
- when this leaf closes, update the parent task summary so the parser and
  diagnostic plumbing change is captured explicitly
