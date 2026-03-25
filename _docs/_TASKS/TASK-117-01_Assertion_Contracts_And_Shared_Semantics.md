# TASK-117-01: Assertion Contracts and Shared Semantics

**Parent:** [TASK-117](./TASK-117_Truth_Layer_Assertion_Wave.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

---

## Objective

Define the shared assertion contract shape before adding individual
`scene_assert_*` tools.

---

## Repository Touchpoints

- `server/adapters/mcp/contracts/scene.py`
- `server/adapters/mcp/areas/scene.py`
- `server/domain/tools/scene.py`
- `server/application/tool_handlers/scene_handler.py`
- `blender_addon/application/handlers/scene.py`
- `tests/unit/tools/scene/`

---

## Leaf Breakdown

| Leaf | Purpose |
|------|---------|
| [TASK-117-01-01](./TASK-117-01-01_Shared_Assertion_Result_Envelope.md) | Shared pass/fail payload for all assertion tools |
| [TASK-117-01-02](./TASK-117-01-02_Tolerance_And_Comparator_Semantics.md) | Explicit tolerance/comparator rules and numeric semantics |

---

## Acceptance Criteria

- all assertion tools can share one compact result vocabulary
- expected/actual/tolerance semantics are defined before per-tool implementation
