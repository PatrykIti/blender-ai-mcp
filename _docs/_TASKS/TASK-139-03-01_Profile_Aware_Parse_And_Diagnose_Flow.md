# TASK-139-03-01: Profile-Aware Parse and Diagnose Flow

**Parent:** [TASK-139-03](./TASK-139-03_Parser_Repair_And_Diagnostics_By_Contract_Profile.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Thread the resolved contract profile through `parse_vision_output_text(...)` and
`diagnose_vision_output_text(...)` so repair and classification can key off the
selected profile instead of provider identity alone.

## Repository Touchpoints

- `server/adapters/mcp/vision/parsing.py`
- `server/adapters/mcp/vision/backends.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`

## Acceptance Criteria

- parser/diagnostic entry points accept the selected contract profile
- provider-only repair branching is removed or reduced where contract-profile
  branching is the real intent
- diagnostics still expose `container_shape` and `payload_shape` without
  losing the current failure classification

## Leaf Work Items

- add contract-profile plumbing through the parser/diagnostic call chain
- keep backward compatibility for existing callers where possible
- expand unit coverage for profile-aware diagnostics

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_parsing.py`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped
