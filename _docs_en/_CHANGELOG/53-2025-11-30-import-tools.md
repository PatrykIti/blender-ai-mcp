# 53 - Import Tools (TASK-035)

**Date:** 2025-11-30
**Version:** 1.26.0

## Summary

Implemented **TASK-035: Import Tools** - File import operations to bring external 3D assets, images, and reference materials into Blender. Complements existing export tools.

## Changes

### New Tools (4)

| Tool | Description |
|------|-------------|
| `import_obj` | Imports OBJ file (geometry, UVs, normals, materials) |
| `import_fbx` | Imports FBX file (geometry, materials, animations, armatures) |
| `import_glb` | Imports GLB/GLTF file (PBR materials, animations) |
| `import_image_as_plane` | Imports image as textured plane (reference images, decals) |

### Files Created

**Server Side:**
- `server/domain/tools/import_tool.py` - IImportTool interface with 4 abstract methods
- `server/application/tool_handlers/import_handler.py` - RPC bridge implementation
- `server/adapters/mcp/areas/import_tool.py` - 4 MCP tool definitions

**Blender Addon:**
- `blender_addon/application/handlers/import_handler.py` - Blender API implementations

### Files Modified

- `server/infrastructure/di.py` - Added get_import_handler provider
- `server/adapters/mcp/areas/__init__.py` - Registered import_tool module
- `blender_addon/__init__.py` - Registered 4 RPC handlers

### Tests

- `tests/unit/tools/import_tool/test_import_handler.py` - 13 unit tests
- `tests/e2e/tools/import_tool/test_import_tools.py` - E2E roundtrip tests

## RPC Handlers Registered

| RPC Command | Handler Method |
|-------------|----------------|
| `import.obj` | `import_obj` |
| `import.fbx` | `import_fbx` |
| `import.glb` | `import_glb` |
| `import.image_as_plane` | `import_image_as_plane` |

## Use Cases

- **import_obj**: Loading client meshes, CAD exports, cross-software workflows
- **import_fbx**: Game engine assets, animated characters, industry standard interchange
- **import_glb**: Web 3D assets, Sketchfab downloads, modern PBR workflows
- **import_image_as_plane**: Reference blueprints, concept art, background plates

## Features

- File existence validation before import
- Returns list of imported object names
- `import_image_as_plane` auto-enables required addon if not already enabled
- Supports axis configuration for different coordinate systems
- Optional scale factor for imported geometry

## Testing

- 13 unit tests (all passing)
- E2E tests covering:
  - OBJ roundtrip (export → clear → import → verify)
  - FBX roundtrip
  - GLB roundtrip
  - Image as plane import
  - Error handling for missing files
