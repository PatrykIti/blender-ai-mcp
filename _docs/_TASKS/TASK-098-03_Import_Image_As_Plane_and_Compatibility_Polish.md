# TASK-098-03: Import Image As Plane and Compatibility Polish

**Parent:** [TASK-098](./TASK-098_Background_Task_Adoption_for_Import_Export.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-098-02](./TASK-098-02_Import_Task_Mode_Adoption.md)

---

## Objective

Make the task-mode decision for `import_image_as_plane` explicit and close the remaining compatibility edge cases around the import/export extension wave.

---

## Repository Touchpoints

- `server/adapters/mcp/areas/system.py`
- `server/application/tool_handlers/system_handler.py`
- `blender_addon/application/handlers/system.py`
- `tests/unit/tools/import_tool/`
- `tests/e2e/tools/import_tool/`

---

## Planned Work

- decide whether `import_image_as_plane` stays foreground-only or joins the task-enabled import family
- align docstrings, compatibility behavior, and surface guidance with that decision

### Current Code Reality

`import_image_as_plane` is materially different from the pure importer wrappers:

- it loads an image
- creates plane geometry
- creates a material and shader node graph
- assigns transforms and orientation

So this slice should not inherit candidacy automatically just because it lives in the same MCP area.

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-098-03-01](./TASK-098-03-01_Core_Import_Image_As_Plane_Candidacy_Adoption.md) | Core Import Image As Plane Candidacy and Adoption | Core implementation layer |
| [TASK-098-03-02](./TASK-098-03-02_Tests_Import_Image_As_Plane_Compatibility_Polish.md) | Tests and Docs Import Image As Plane Compatibility Polish | Tests, docs, and QA |

---

## Acceptance Criteria

- `import_image_as_plane` has an explicit, documented task-mode stance
- compatibility/docs polish is complete for the import/export extension wave
