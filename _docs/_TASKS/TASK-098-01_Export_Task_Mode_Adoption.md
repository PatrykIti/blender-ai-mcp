# TASK-098-01: Export Task Mode Adoption

**Parent:** [TASK-098](./TASK-098_Background_Task_Adoption_for_Import_Export.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-088](./TASK-088_Background_Tasks_and_Progress.md)

---

## Objective

Adopt background task mode for the export tool family by reusing the TASK-088 bridge and addon job lifecycle.

---

## Repository Touchpoints

- `server/adapters/mcp/areas/system.py`
- `server/application/tool_handlers/system_handler.py`
- `blender_addon/application/handlers/system.py`
- `blender_addon/__init__.py`
- `blender_addon/infrastructure/rpc_server.py`
- `tests/unit/tools/export/`
- `tests/e2e/tools/export/`

---

## Planned Work

- adopt:
  - `export_glb`
  - `export_fbx`
  - `export_obj`

### Current Code Reality

- `export_glb` and `export_fbx` are straightforward exporter calls with extension normalization and directory creation
- `export_obj` has extra validation and post-export verification:
  - writable directory check
  - mesh-object presence guard
  - explicit file existence verification after exporter success

### Adoption Rule

Exports should follow the same pattern as the TASK-088 first wave:

- explicit async MCP entrypoints
- `TaskConfig(mode="optional")`
- addon-side cooperative progress/cancel hooks
- synchronous fallback preserved for non-task surfaces
- `OBJ`-specific validation and file verification must survive unchanged

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-098-01-01](./TASK-098-01-01_Core_Export_Task_Mode_Adoption.md) | Core Export Task Mode Adoption | Core implementation layer |
| [TASK-098-01-02](./TASK-098-01-02_Tests_Export_Task_Mode_Adoption.md) | Tests and Docs Export Task Mode Adoption | Tests, docs, and QA |

---

## Acceptance Criteria

- export tools can run through the shared background task path
- export tools keep a coherent synchronous fallback path
