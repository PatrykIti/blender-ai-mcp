# 51 - Baking Tools (TASK-031)

**Date:** 2025-11-30
**Version:** 1.24.0

## Summary

Implemented **TASK-031: Baking Tools** - Critical tools for game development workflows. These tools enable texture baking operations using Blender's Cycles renderer.

## Changes

### New Tools (4)

| Tool | Description |
|------|-------------|
| `bake_normal_map` | Bakes normal map from geometry or high-poly to low-poly |
| `bake_ao` | Bakes ambient occlusion map |
| `bake_combined` | Bakes full render (material + lighting) to texture |
| `bake_diffuse` | Bakes diffuse/albedo color only |

### New Files

**Server Side:**
- `server/domain/tools/baking.py` - IBakingTool interface
- `server/application/tool_handlers/baking_handler.py` - RPC bridge implementation
- `server/adapters/mcp/areas/baking.py` - MCP tool definitions

**Blender Addon:**
- `blender_addon/application/handlers/baking.py` - BakingHandler class

**Tests:**
- `tests/unit/tools/baking/test_baking_handler.py` - 14 unit tests
- `tests/e2e/tools/baking/test_baking_tools.py` - E2E test suite

### Modified Files

- `server/infrastructure/di.py` - Added `get_baking_handler` provider
- `server/adapters/mcp/areas/__init__.py` - Import baking module
- `blender_addon/__init__.py` - Registered 4 RPC handlers

## Features

- **Cycles Auto-Switch**: Automatically switches to Cycles renderer (required for baking)
- **UV Validation**: Validates UV maps exist with helpful error messages
- **Material Auto-Setup**: Creates bake target material/node if missing
- **Multiple Formats**: Supports PNG, JPEG, and EXR output
- **High-to-Low Baking**: Supports baking from high-poly source with cage extrusion
- **Normal Spaces**: Supports both TANGENT and OBJECT space normal maps
- **Configurable**: Resolution, samples, margin, lighting passes

## RPC Handlers Registered

| RPC Command | Handler Method |
|-------------|----------------|
| `baking.normal_map` | `bake_normal_map` |
| `baking.ao` | `bake_ao` |
| `baking.combined` | `bake_combined` |
| `baking.diffuse` | `bake_diffuse` |

## Testing

- 14 unit tests (all passing)
- E2E tests covering:
  - Normal map self-bake
  - High-to-low poly baking
  - AO baking with custom samples
  - Combined baking with lighting passes
  - Diffuse color baking
  - Complete game asset baking workflow
  - Missing UV error handling
