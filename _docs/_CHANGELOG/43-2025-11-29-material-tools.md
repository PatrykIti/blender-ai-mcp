# Changelog #43 - Material Tools (TASK-023)

**Date:** 2025-11-29
**Version:** 1.16.0
**Category:** Feature Implementation

---

## Overview

Implemented complete Material Tools for PBR workflows, enabling AI to create, assign, modify, and texture materials using Blender's Principled BSDF shader.

## Changes

### New MCP Tools

| Tool | Description |
|------|-------------|
| `material_create` | Creates new PBR material with Principled BSDF shader |
| `material_assign` | Assigns material to object or selected faces |
| `material_set_params` | Modifies existing material parameters |
| `material_set_texture` | Binds image texture to material input |

### Implementation Details

**Server-Side:**
- Extended `IMaterialTool` interface in Domain Layer
- Implemented `MaterialToolHandler` with RPC bridge
- Added MCP tool definitions with semantic tags

**Addon-Side:**
- Extended `MaterialHandler` with 4 new methods
- Registered RPC handlers for material operations

### Files Changed

**Server:**
- `server/domain/tools/material.py` - Extended interface
- `server/application/tool_handlers/material_handler.py` - RPC bridge
- `server/adapters/mcp/areas/material.py` - MCP definitions

**Addon:**
- `blender_addon/application/handlers/material.py` - Blender implementation
- `blender_addon/__init__.py` - RPC handler registration

**Tests:**
- `tests/unit/tools/material/test_material_tools.py` - Unit tests (14 tests)
- `tests/e2e/tools/material/test_material_tools.py` - E2E tests (12 tests)

## Testing

- 14 unit tests passing
- 12 E2E tests ready (requires Blender addon activation)

## Notes

- Materials use Principled BSDF shader by default
- Alpha < 1.0 automatically sets blend mode to BLEND
- Normal maps automatically get Normal Map node
- Non-color textures (roughness, metallic) auto-switch color space

---

*Related Tasks: TASK-023-1, TASK-023-2, TASK-023-3, TASK-023-4*
