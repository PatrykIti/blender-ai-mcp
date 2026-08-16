# TASK-092-06-01: Core Scene State Assistant Summaries

**Parent:** [TASK-092-06](./TASK-092-06_Scene_State_Assistant_Summaries.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium

---

## Objective

Implement bounded assistant summaries for the next wave of structured scene-state tools.

---

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/adapters/mcp/transforms/public_params.py`

---

## Acceptance Criteria

- `scene_snapshot_state`
- `scene_compare_snapshot`
- `scene_get_hierarchy`
- `scene_get_bounding_box`
- `scene_get_origin_info`

all accept an internal/expert-only `assistant_summary` flag and attach a typed bounded summary envelope.
