# TASK-112-01: Deterministic Region Falloff Engine

**Priority:** 🟡 Medium  
**Category:** Sculpt Core  
**Estimated Effort:** Medium  
**Dependencies:** TASK-112  
**Status:** ⏳ To Do

---

## Objective

Build the shared deterministic geometry engine used by the programmatic sculpt tools.

---

## Scope

- define one shared region parameter model:
  - `object_name`
  - `center`
  - `radius`
  - `strength`
  - `falloff`
  - `symmetry`
- implement vertex collection within radius
- implement deterministic falloff functions:
  - `SMOOTH`
  - `LINEAR`
  - `SHARP`
  - optional `CONSTANT`
- implement optional symmetry application on X/Y/Z
- expose a reusable Blender-side helper instead of duplicating logic per tool

---

## Repository Touchpoints

- `server/domain/tools/sculpt.py`
- `server/application/tool_handlers/sculpt_handler.py`
- `blender_addon/application/handlers/sculpt.py`
- `tests/unit/tools/sculpt/`

---

## Acceptance Criteria

- one shared region/falloff implementation exists for later sculpt tools
- falloff behavior is deterministic and unit-tested
- symmetry behavior is deterministic and unit-tested
