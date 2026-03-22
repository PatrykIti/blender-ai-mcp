# TASK-098-02: Import Task Mode Adoption

**Parent:** [TASK-098](./TASK-098_Background_Task_Adoption_for_Import_Export.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-088](./TASK-088_Background_Tasks_and_Progress.md)

---

## Objective

Adopt background task mode for the main import tool family on top of the TASK-088 runtime model.

---

## Repository Touchpoints

- `server/adapters/mcp/areas/system.py`
- `server/application/tool_handlers/system_handler.py`
- `blender_addon/application/handlers/system.py`
- `blender_addon/__init__.py`
- `blender_addon/infrastructure/rpc_server.py`
- `tests/unit/tools/import_tool/`
- `tests/e2e/tools/import_tool/`

---

## Planned Work

- adopt:
  - `import_obj`
  - `import_fbx`
  - `import_glb`

### Current Code Reality

- all three imports track objects before/after import and report imported object deltas
- `import_obj` uses `bpy.ops.wm.obj_import`
- `import_fbx` uses `bpy.ops.import_scene.fbx`
- `import_glb` uses `bpy.ops.import_scene.gltf`

### Adoption Rule

Imports must reuse the same task-mode semantics and control plane already introduced for renders, extraction, workflow import, and export extension work.

Foreground result strings that mention imported object names should remain understandable and stable.

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-098-02-01](./TASK-098-02-01_Core_Import_Task_Mode_Adoption.md) | Core Import Task Mode Adoption | Core implementation layer |
| [TASK-098-02-02](./TASK-098-02-02_Tests_Import_Task_Mode_Adoption.md) | Tests and Docs Import Task Mode Adoption | Tests, docs, and QA |

---

## Acceptance Criteria

- import tools can run through the shared background task path
- import tools keep a coherent synchronous fallback path
