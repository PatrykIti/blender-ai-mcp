# TASK-122-01-01: Assembled Target Scope and Part Group Contract

**Parent:** [TASK-122-01](./TASK-122-01_Spatial_Correction_Truth_Bundles_For_Assembled_Models.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium

**Completion Summary:** Added a canonical `assembled_target_scope` contract for stage compare and iterate flows. The contract now distinguishes `single_object`, `object_set`, `collection`, and `scene` targeting, and the current response envelopes carry that structured scope instead of leaving downstream consumers to infer meaning only from loose `target_object`, `target_objects`, and `collection_name` fields.

## Objective

Define one stable contract for assembled correction targets, including single parts, multiple parts, named groups, collection-backed groups, and role-based groups such as head/ears/body/tail/limbs.

## Repository Touchpoints

- `server/adapters/mcp/contracts/scene.py`
- `server/adapters/mcp/areas/scene.py`
- `server/application/tool_handlers/scene_handler.py`
- `server/router/application/`
- `tests/unit/tools/scene/`
- `tests/unit/router/`
- `tests/e2e/tools/scene/`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`

## Acceptance Criteria

- assembled target scope can name one object, multiple objects, collection-backed groups, and role-based groups without prose interpretation
- the contract is explicit enough for truth bundles and correction-loop consumers to reuse directly

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md` if the truth-bundle surface changes

## Tests To Add/Update

- `tests/unit/tools/scene/`
- `tests/unit/router/`
- `tests/e2e/tools/scene/` when the shipped behavior depends on real Blender geometry

## Changelog Impact

- add a `_docs/_CHANGELOG/*.md` entry when this leaf changes truth-bundle contracts, loop handoff behavior, or public docs

## Status / Board Update

- this leaf is closed; the parent task and `_docs/_TASKS/README.md` now reflect that `TASK-122` work has started
*** Add File: _docs/_CHANGELOG/182-2026-04-01-assembled-target-scope-contract.md
# 182. Assembled target scope contract

Date: 2026-04-01

## Summary

Started the `TASK-122` reliability wave by adding a canonical assembled-target
scope contract for stage compare and iterate flows.

## What Changed

- added a structured `assembled_target_scope` contract for assembled-model
  targeting
- wired that scope into `reference_compare_stage_checkpoint(...)` and
  `reference_iterate_stage_checkpoint(...)` responses
- classified current targeting modes into:
  - `single_object`
  - `object_set`
  - `collection`
  - `scene`
- added unit coverage for:
  - the new scene contract types
  - stage compare response scope classification
  - capture-bundle compatibility defaults

## Why

The upcoming `TASK-122` truth-bundle and hybrid-loop work needs one stable
scope envelope for assembled targets. Without it, downstream consumers still
have to infer semantics ad hoc from `target_object`, `target_objects`, and
`collection_name`.
