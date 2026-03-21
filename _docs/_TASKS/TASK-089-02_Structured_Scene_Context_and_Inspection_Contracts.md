# TASK-089-02: Structured Scene Context and Inspection Contracts

**Parent:** [TASK-089](./TASK-089_Typed_Contracts_and_Structured_Responses.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-089-01](./TASK-089-01_Contract_Catalog_and_Response_Guidelines.md)

---

## Objective

Expose typed contracts for `scene_context`, `scene_inspect`, `scene_snapshot_state`, `scene_compare_snapshot`, and related read-heavy scene tools.

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
- replace stringified JSON return paths in scene read adapters with native dict / model returns

### State Priority

These contracts should optimize for LLM awareness of:

- active mode
- active object
- selection state
- hierarchy and collections
- transforms, bounds, and origin
- material and modifier context

---

## Pseudocode

```python
class SceneModeContract(BaseModel):
    mode: str
    active_object: str | None
    active_object_type: str | None
    selected_object_names: list[str]
    selection_count: int
```

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-089-02-01](./TASK-089-02-01_Core_Structured_Scene_Context_Inspection.md) | Core Structured Scene Context and Inspection Contracts | Core implementation layer |
| [TASK-089-02-02](./TASK-089-02-02_Tests_Structured_Scene_Context_Inspection.md) | Tests and Docs Structured Scene Context and Inspection Contracts | Tests, docs, and QA |

---

## Acceptance Criteria

- scene read tools return stable structured schemas
- human-readable summaries become an optional presentation layer
- structured surfaces expose scene contracts via `structuredContent` with matching `outputSchema`

---

## Atomic Work Items

1. Define scene-mode and selection contracts first.
2. Return native structured payloads from `scene_context` actions instead of prose-only or JSON-string wrappers.
3. Define object inspection contracts with transforms, bounds, origin, and hierarchy.
4. Define snapshot and diff contracts for before/after awareness.
5. Add tests proving FastMCP surfaces structured MCP output directly from the returned object/model payloads.
