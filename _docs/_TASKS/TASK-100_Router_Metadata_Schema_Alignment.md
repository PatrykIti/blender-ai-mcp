# TASK-100: Router Metadata Schema Alignment for Pre-commit Validation

**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** -

---

## Objective

Align router tool metadata files with the current metadata schema so `check-router-tool-metadata` passes in the repo-wide `pre-commit` suite.

This task exists because the typing/pre-commit baseline is now green for Python (`ruff`, `mypy`, unit tests), but the metadata JSON layer still carries older type labels such as `list[float]`, `boolean`, `integer`, `number`, `dict`, `any`, and `string_or_list` that do not match the current schema enum.

---

## Repository Touchpoints

- `server/router/infrastructure/tools_metadata/_schema.json`
- `server/router/infrastructure/tools_metadata/**/**/*.json`
- `.pre-commit-config.yaml`
- `tests/unit/router/infrastructure/test_metadata_loader.py`
- `tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_MCP_SERVER/README.md`

---

## Planned Work

- inventory the current metadata `parameters.*.type` values used in router metadata files
- decide whether to normalize files to the current schema vocabulary or extend the schema intentionally
- remove legacy aliases such as `boolean`, `integer`, `number`, `dict`, `any`, `string_or_list`, and ad hoc list signatures where they are no longer valid
- keep metadata semantics explicit for vector inputs, arrays, enums, and open-ended payloads
- add regression coverage so metadata/schema drift is caught before new files land

### Current Gap

The repo-level `pre-commit run --all-files` currently reaches the metadata validation hook and fails on schema/type drift in existing router metadata JSON files.

Examples of current mismatches:

- `list[float]`
- `list[int]`
- `list[list[float]]`
- `list[list[int]]`
- `array | string`
- `boolean`
- `integer`
- `number`
- `dict`
- `any`
- `string_or_list`

---

## Acceptance Criteria

- `check-router-tool-metadata` passes on the full repo
- the schema and metadata files use one deliberate shared type vocabulary
- vector and list-valued parameters are represented consistently
- tests cover schema drift for newly added metadata files
- documentation reflects the chosen metadata type model

## Completion Summary

- normalized legacy metadata aliases such as `boolean`, `integer`, `number`, `list[float]`, `list[int]`, `list[string]`, `list[list[float]]`, `list[list[int]]`, `string_or_list`, and mixed `list[...] | string` forms
- standardized coordinate-style inputs onto `vector3`, open lists onto `array`, and kept scalar primitives on `string/int/float/bool`
- extended the metadata schema deliberately with `object` and `scalar` for the two remaining real semantic cases:
  - structured modifier property maps
  - custom property values that can be one primitive scalar
- repo-level `pre-commit run --all-files` now passes, including `check-router-tool-metadata`

## Notes

- This task was split out while adding the repo-wide `mypy` baseline and `pre-commit` typing hook, so the Python/tooling cleanup could ship independently from the older metadata backlog.
