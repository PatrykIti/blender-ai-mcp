# TASK-122-01-01: Assembled Target Scope and Part Group Contract

**Parent:** [TASK-122-01](./TASK-122-01_Spatial_Correction_Truth_Bundles_For_Assembled_Models.md)  
**Status:** ⏳ To Do  
**Priority:** 🟡 Medium

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

- update this leaf, its parent task, and `_docs/_TASKS/README.md` when the work starts or closes
