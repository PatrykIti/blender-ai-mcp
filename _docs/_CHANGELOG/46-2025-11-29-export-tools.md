# Changelog #46 - Export Tools (TASK-026)

**Date:** 2025-11-29
**Version:** 1.19.0

## Summary

Implemented file export tools for common 3D formats (GLB/GLTF, FBX, OBJ).

## Changes

### New Tools

| Tool | Description |
|------|-------------|
| `export_glb` | Export to GLB/GLTF format (web, game engines) |
| `export_fbx` | Export to FBX format (industry standard) |
| `export_obj` | Export to OBJ format (universal mesh) |

### Implementation Details

#### export_glb
- Supports GLB (binary) and GLTF (separate files) formats
- Options: `export_selected`, `export_animations`, `export_materials`, `apply_modifiers`
- Auto-creates directories if needed
- Ideal for web and game engines (Unity, Unreal, Godot)

#### export_fbx
- Industry standard format for DCC interchange
- Options: `export_selected`, `export_animations`, `apply_modifiers`, `mesh_smooth_type`
- Smooth types: OFF, FACE, EDGE
- Optimized bone axis settings for game engines

#### export_obj
- Universal mesh format supported by virtually all 3D software
- Options: `export_selected`, `apply_modifiers`, `export_materials`, `export_uvs`, `export_normals`, `triangulate`
- Creates .obj (geometry) and .mtl (materials) files

### Files Added/Modified

**Server:**
- `server/domain/tools/export.py` - IExportTool interface
- `server/application/tool_handlers/export_handler.py` - ExportToolHandler
- `server/adapters/mcp/areas/export.py` - MCP tool definitions
- `server/infrastructure/di.py` - get_export_handler()
- `server/adapters/mcp/areas/__init__.py` - export import

**Blender Addon:**
- `blender_addon/application/handlers/export.py` - ExportHandler
- `blender_addon/__init__.py` - RPC handler registration

**Tests:**
- `tests/unit/tools/export/__init__.py`
- `tests/unit/tools/export/test_export_tools.py` - 33 unit tests
- `tests/e2e/tools/export/__init__.py`
- `tests/e2e/tools/export/test_export_tools.py` - E2E tests

### Test Coverage

- 33 unit tests covering all export methods and edge cases
- E2E tests prepared for manual execution with running Blender

## Task Reference

- [TASK-026-1: export_glb](../_TASKS/TASK-026_Export_Tools.md#task-026-1-export_glb) ✅
- [TASK-026-2: export_fbx](../_TASKS/TASK-026_Export_Tools.md#task-026-2-export_fbx) ✅
- [TASK-026-3: export_obj](../_TASKS/TASK-026_Export_Tools.md#task-026-3-export_obj) ✅
