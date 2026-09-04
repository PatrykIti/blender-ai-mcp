# TASK-116-01: Distance and Dimensions

**Parent:** [TASK-116](./TASK-116_First_Measure_Assert_Code_Wave.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** `scene_measure_distance` and `scene_measure_dimensions` are now implemented through addon, handler, dispatcher, MCP adapter, metadata, docs, and tests.

---

## Objective

Implement the first two smallest truth-layer atomics:

- `scene_measure_distance`
- `scene_measure_dimensions`

---

## Repository Touchpoints

- `server/domain/tools/scene.py`
- `server/application/tool_handlers/scene_handler.py`
- `blender_addon/application/handlers/scene.py`
- `blender_addon/__init__.py`
- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/dispatcher.py`
- `server/router/infrastructure/tools_metadata/scene/`
- `tests/unit/tools/scene/`
- `tests/e2e/tools/scene/`

---

## Contract Direction

`scene_measure_distance`

- object-to-object distance
- origin-to-origin distance as initial baseline
- compact output:
  - `from`
  - `to`
  - `distance`
  - `units`

`scene_measure_dimensions`

- object dimensions
- compact output:
  - `object_name`
  - `dimensions`
  - `world_space`
  - `units`

---

## Acceptance Criteria

- both tools work end-to-end through addon, handler, adapter, and dispatcher
- both tools return compact structured outputs
- both tools are suitable for LLM verification flows
