# Changelog: Material Tools (TASK-014-8 & 014-9)

## Added
- New domain layer `server/domain/tools/material.py` with `IMaterialTool` interface.
- Material handler implementations:
  - `blender_addon/application/handlers/material.py` - MaterialHandler with list_materials and list_by_object
  - `server/application/tool_handlers/material_handler.py` - MaterialToolHandler for RPC
- MCP tools:
  - `material_list` - lists materials with shader parameters and assignment counts
  - `material_list_by_object` - lists material slots for a given object
- Principled BSDF parameter extraction (base_color, roughness, metallic, alpha)
- DI provider `get_material_handler()` in `server/infrastructure/di.py`
- RPC endpoints registered in `blender_addon/__init__.py`

## Documentation
- Updated task board statistics
- Created MATERIAL_TOOLS_ARCHITECTURE.md
- Added material tools to available tools summary

## Version
1.9.8
