# TASK-098-03-01: Core Import Image As Plane Candidacy and Adoption

**Parent:** [TASK-098-03](./TASK-098-03_Import_Image_As_Plane_and_Compatibility_Polish.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-098-02](./TASK-098-02_Import_Task_Mode_Adoption.md)

---

## Objective

Implement the chosen execution-mode strategy for `import_image_as_plane`.

---

## Repository Touchpoints

- `server/adapters/mcp/areas/system.py`
- `server/application/tool_handlers/system_handler.py`
- `blender_addon/application/handlers/system.py`

---

## Planned Work

- decide candidacy explicitly:
  - foreground-only
  - task-optional
- implement the chosen behavior without introducing a special-case execution model

### Decision Inputs

- current handler is a custom multi-step construction flow, not a direct Blender importer wrapper
- existing unit/E2E tests already exercise its geometry/material behavior
- the task decision should be driven by observed blocking risk and UX value, not by taxonomy alone

---

## Acceptance Criteria

- `import_image_as_plane` is no longer ambiguous in the task-mode architecture
