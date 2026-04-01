# TASK-089-02-01: Core Structured Scene Context and Inspection Contracts

**Parent:** [TASK-089-02](./TASK-089-02_Structured_Scene_Context_and_Inspection_Contracts.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-089-01](./TASK-089-01_Contract_Catalog_and_Response_Guidelines.md)

---

## Objective

Implement the core code changes for **Structured Scene Context and Inspection Contracts**.

---

## Repository Touchpoints

- `server/application/tool_handlers/scene_handler.py`
- `server/adapters/mcp/areas/scene.py`
- `server/domain/tools/scene.py`

---

## Planned Work

- create:
  - `server/adapters/mcp/contracts/scene.py`
  - `tests/unit/tools/scene/test_scene_contracts.py`
- reduce prose formatting in helpers such as:
  - `_scene_get_mode`
  - `_scene_list_selection`
  - `_scene_inspect_object`

### State Priority

These contracts should optimize for LLM awareness of:

- active mode
- active object
- selection state
- hierarchy and collections
- transforms, bounds, and origin
- material and modifier context
---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-089-02-01-01](./TASK-089-02-01-01_Scene_Contract_Definitions.md) | Scene Contract Definitions | Core slice |
| [TASK-089-02-01-02](./TASK-089-02-01-02_Handler_and_Adapter_Integration.md) | Handler and Adapter Integration | Core slice |

---

## Acceptance Criteria

- scene read tools return stable structured schemas
- human-readable summaries become an optional presentation layer
---

## Atomic Work Items

1. Define scene-mode and selection contracts first.
2. Define object inspection contracts with transforms, bounds, origin, and hierarchy.
3. Define snapshot and diff contracts for before/after awareness.
4. Add tests proving the same payload can be rendered with or without summary text.
