# TASK-092-06: Scene State Assistant Summaries

**Parent:** [TASK-092](./TASK-092_Server_Side_Sampling_Assistants.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-092-03](./TASK-092-03_Inspection_Summarizer_and_Repair_Suggester_Assistants.md)

---

## Objective

Extend bounded `assistant_summary` support from the initial inspection tools to the next wave of structured scene-state read surfaces.

---

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/adapters/mcp/transforms/public_params.py`
- `tests/unit/tools/scene/`

---

## Target Tools

- `scene_snapshot_state`
- `scene_compare_snapshot`
- `scene_get_hierarchy`
- `scene_get_bounding_box`
- `scene_get_origin_info`

---

## Acceptance Criteria

- each listed tool can optionally attach a bounded typed assistant summary
- the assistant remains subordinate to the structured scene-state payload
- `assistant_summary` stays hidden on `llm-guided`

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-092-06-01](./TASK-092-06-01_Core_Scene_State_Assistant_Summaries.md) | Core Scene State Assistant Summaries | Core implementation layer |
| [TASK-092-06-02](./TASK-092-06-02_Tests_Scene_State_Assistant_Summaries.md) | Tests and Docs Scene State Assistant Summaries | Tests, docs, and QA |
