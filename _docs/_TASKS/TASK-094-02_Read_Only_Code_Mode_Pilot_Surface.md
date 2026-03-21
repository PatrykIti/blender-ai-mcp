# TASK-094-02: Read-Only Code Mode Pilot Surface

**Parent:** [TASK-094](./TASK-094_Code_Mode_Exploration.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-094-01](./TASK-094-01_Code_Mode_Experiment_Design_and_Guardrails.md)

---

## Objective

Build a read-only pilot surface for discovery, inspection, and workflow exploration use cases.

---

## Repository Touchpoints

- `server/application/tool_handlers/scene_handler.py`
- `server/application/tool_handlers/mesh_handler.py`
- `server/application/tool_handlers/workflow_catalog_handler.py`

---

## Acceptance Criteria

- the pilot surface does not expose direct destructive write paths by default
