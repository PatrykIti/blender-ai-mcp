# Changelog: Tool Docstring Standardization (TASK-011-5, 011-6, 011-7)

## Updated
- **All `mesh_*` tools** (TASK-011-5):
  - Added semantic tags: `[EDIT MODE][SELECTION-BASED][DESTRUCTIVE]` or `[SAFE]`.
  - Clarified selection semantics and destructiveness.
  - Added TIP in `mesh_boolean` to prefer `modeling_add_modifier(BOOLEAN)` for object-level booleans.
  - Updated both MCP server (`server/adapters/mcp/server.py`) and Blender addon (`blender_addon/application/handlers/mesh.py`).

- **All `modeling_*` tools** (TASK-011-6):
  - Added semantic tags: `[OBJECT MODE][SAFE][NON-DESTRUCTIVE]` or `[DESTRUCTIVE]`.
  - Clarified safe vs destructive operations.
  - Emphasized `modeling_add_modifier` as preferred high-level method for non-destructive workflows.
  - Updated both MCP server and Blender addon (`blender_addon/application/handlers/modeling.py`).

- **All `scene_*` tools** (TASK-011-7):
  - Added semantic tags: `[SCENE][SAFE]` or `[DESTRUCTIVE]`.
  - Added explicit warnings for destructive tools (`scene_clean_scene`, `scene_delete_object`).
  - Updated MCP server (`server/adapters/mcp/server.py`).

## Impact
- **Token-cheap** semantic tags help LLMs understand tool context, safety, and required preconditions.
- Consistent tagging across 30+ tools reduces AI errors and improves workflow planning.
- Clear warnings prevent accidental data loss (e.g., boolean operations, scene cleaning).
