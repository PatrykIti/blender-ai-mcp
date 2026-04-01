# TASK-117-02: First Assertion Tools, Contact and Dimensions

**Parent:** [TASK-117](./TASK-117_Truth_Layer_Assertion_Wave.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** `scene_assert_contact` and `scene_assert_dimensions` are now implemented end-to-end across addon, handler, MCP adapter, dispatcher, metadata, docs, and regression coverage.

---

## Objective

Implement the first two smallest assertion tools:

- `scene_assert_contact`
- `scene_assert_dimensions`

These are the most direct follow-up to `TASK-116`.

---

## Repository Touchpoints

- `server/domain/tools/scene.py`
- `server/application/tool_handlers/scene_handler.py`
- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/dispatcher.py`
- `blender_addon/application/handlers/scene.py`
- `blender_addon/__init__.py`
- `server/router/infrastructure/tools_metadata/scene/`
- `tests/unit/tools/scene/`
- `tests/e2e/tools/scene/`

---

## Leaf Breakdown

| Leaf | Purpose |
|------|---------|
| [TASK-117-02-01](./TASK-117-02-01_Scene_Assert_Contact.md) | Pass/fail contact assertion on top of gap/overlap measurement |
| [TASK-117-02-02](./TASK-117-02-02_Scene_Assert_Dimensions.md) | Pass/fail dimension assertion against expected values or ranges |

---

## Acceptance Criteria

- both tools work end-to-end through addon, handler, adapter, and dispatcher
- both tools return compact pass/fail payloads with expected vs actual values
