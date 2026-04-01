# TASK-118-01-02: Scene Inspect World

**Parent:** [TASK-118-01](./TASK-118-01_Read_Side_Scene_State_Expansion.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium

**Completion Summary:** `scene_inspect(action="world")` is now implemented with structured world/background state, including node-based world summary fields when available.

---

## Objective

Add grouped read-side inspection for world/background configuration.

---

## Design Direction

The first implementation should expose:

- world name
- `use_nodes`
- background strength/color basics when simple
- node-graph reference/handoff fields when node-based setup exists

This tool should describe world state cleanly without pretending to rebuild full
node graphs inline.

---

## Acceptance Criteria

- world inspection exposes stable reconstruction-relevant state
- node-based worlds are represented through a clear boundary, not prose blobs
