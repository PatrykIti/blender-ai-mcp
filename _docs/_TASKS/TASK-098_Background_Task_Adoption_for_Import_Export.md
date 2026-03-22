# TASK-098: Background Task Adoption for Import and Export Operations

**Priority:** 🔴 High  
**Category:** FastMCP Operations  
**Estimated Effort:** Medium  
**Dependencies:** TASK-088, TASK-093-02  
**Status:** ✅ Done

**Completion Summary:** This task is now closed. The system import/export family uses explicit async MCP entrypoints with `TaskConfig(mode="optional")`, addon-side background job registration, and the shared TASK-088 bridge. That now includes `export_glb`, `export_fbx`, `export_obj`, `import_obj`, `import_fbx`, `import_glb`, and `import_image_as_plane`, plus task-mode docs/rollback guidance and regression notes.

---

## Objective

Extend the TASK-088 background-task model to the import/export tool family so large file I/O stops relying only on foreground request/response execution.

---

## Problem

TASK-088 established the task bridge, registry, RPC job lifecycle, and the first adopted heavy-operation slices.

Import/export tools still remain outside that adoption wave:

- large OBJ / FBX / GLB imports can block the client loop
- exports can take long enough that cancellation and progress matter
- the task architecture now exists, but the highest-value file operations are not yet consuming it

If they stay outside the rollout too long, the repo ends up with one background model for renders/extraction and a second de facto product expectation for file operations.

---

## Business Outcome

Make heavyweight file interchange feel like a first-class product path rather than a blocking exception.

This enables:

- observable import/export progress
- explicit cancellation for long-running file operations
- reuse of the current TASK-088 control plane instead of growing a second execution model
- a more coherent operations story for future asset and reconstruction pipelines

---

## Proposed Solution

Use the TASK-088 task bridge and RPC job lifecycle as the only background-execution path for the first import/export extension wave.

Adoption should proceed in a strict order:

1. export family
2. import family
3. `import_image_as_plane`
4. docs, rollback notes, and operations guidance

### Current Code Reality

Today the whole import/export family is concentrated in one vertical slice:

- MCP adapters in `server/adapters/mcp/areas/system.py`
- sync server handlers in `server/application/tool_handlers/system_handler.py`
- addon implementations in `blender_addon/application/handlers/system.py`
- addon RPC registration in `blender_addon/__init__.py`

There is also existing test coverage worth reusing instead of inventing a new harness:

- unit export tests in `tests/unit/tools/export/`
- unit import tests in `tests/unit/tools/import_tool/`
- E2E export tests in `tests/e2e/tools/export/`
- E2E import tests in `tests/e2e/tools/import_tool/`

---

## Implementation Constraints

Follow [FASTMCP_3X_IMPLEMENTATION_MODEL.md](./FASTMCP_3X_IMPLEMENTATION_MODEL.md).

This task must reuse the architecture already established by TASK-088:

- no second job registry
- no parallel timeout taxonomy
- no tool-specific ad hoc cancellation protocol
- keep current foreground result strings and path validation semantics readable

Do not flatten the real implementation differences between the tools:

- `export_obj` / `import_obj` use `bpy.ops.wm.obj_*`
- `export_fbx` / `import_fbx` use `bpy.ops.export_scene.fbx` / `bpy.ops.import_scene.fbx`
- `export_glb` / `import_glb` use `bpy.ops.export_scene.gltf` / `bpy.ops.import_scene.gltf`
- `import_image_as_plane` is a custom geometry/material construction flow, not a plain importer wrapper

Keep the distinction explicit between:

- candidacy already established in TASK-088
- actual adoption in MCP adapters and addon job handlers

Task mode should stay:

- `TaskConfig(mode="optional")` for the initial import/export rollout
- `async def` at the MCP boundary
- understandable in synchronous fallback mode on non-task/legacy surfaces

---

## Scope

This task covers:

- `export_glb`
- `export_fbx`
- `export_obj`
- `import_obj`
- `import_fbx`
- `import_glb`
- `import_image_as_plane`
- operations/docs/rollback notes for the import/export task-mode rollout

This task does not cover:

- image asset pipeline redesign
- new task families outside import/export
- replacing the TASK-088 bridge with a different runtime model

---

## Why This Matters For Blender AI

Import/export is one of the clearest places where long-running work becomes visible to users.

If renders and extraction can run as observable background work but file interchange cannot, the product still feels inconsistent at exactly the moment when users are moving data in and out of Blender.

---

## Success Criteria

- Export tools support background task mode through the existing task bridge.
- Import tools support background task mode through the existing task bridge.
- `import_image_as_plane` has an explicit decision and rollout path instead of being left ambiguous.
- The repo documents the import/export task-mode extension and its rollback/compatibility boundaries.

---

## Umbrella Execution Notes

This remains the umbrella task. The original scope stays unchanged.

### Atomic Delivery Waves

1. Adopt export tools to the TASK-088 background execution model.
2. Adopt import tools to the TASK-088 background execution model.
3. Decide and implement `import_image_as_plane` task behavior explicitly.
4. Close the extension with rollback notes, operations guidance, and tests/docs.

Implementation is decomposed into:

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-098-01](./TASK-098-01_Export_Task_Mode_Adoption.md) | Adopt background task mode for export tools |
| 2 | [TASK-098-02](./TASK-098-02_Import_Task_Mode_Adoption.md) | Adopt background task mode for import tools |
| 3 | [TASK-098-03](./TASK-098-03_Import_Image_As_Plane_and_Compatibility_Polish.md) | Decide and implement task behavior for `import_image_as_plane` |
| 4 | [TASK-098-04](./TASK-098-04_Operations_Rollback_and_Documentation.md) | Finalize rollback notes, operations docs, and regression coverage |
