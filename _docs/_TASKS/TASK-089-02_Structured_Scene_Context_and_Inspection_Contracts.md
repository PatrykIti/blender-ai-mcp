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

## Acceptance Criteria

- scene read tools return stable structured schemas
- human-readable summaries become an optional presentation layer
