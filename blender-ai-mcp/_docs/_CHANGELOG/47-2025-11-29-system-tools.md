# Changelog 47: System Tools (TASK-025)

**Date:** 2025-11-29
**Version:** 1.20.0

---

## Summary

Implemented system-level tools for mode switching, undo/redo, file operations, and checkpoint management.

---

## New Tools

### System Tools (`system_*`)

| Tool | Description | Tags |
|------|-------------|------|
| `system_set_mode` | Switches Blender mode (OBJECT/EDIT/SCULPT/POSE/...) with optional object selection | `[SCENE][SAFE]` |
| `system_undo` | Undoes last operation(s), max 10 steps | `[SCENE][NON-DESTRUCTIVE]` |
| `system_redo` | Redoes previously undone operation(s), max 10 steps | `[SCENE][NON-DESTRUCTIVE]` |
| `system_save_file` | Saves current .blend file (with optional filepath) | `[SCENE][DESTRUCTIVE]` |
| `system_new_file` | Creates new file (resets scene) | `[SCENE][DESTRUCTIVE]` |
| `system_snapshot` | Manages quick save/restore checkpoints (save/restore/list/delete) | `[SCENE][NON-DESTRUCTIVE]` |

---

## Implementation Details

### Architecture (4 Layers)

1. **Domain Layer** (`server/domain/tools/system.py`)
   - `ISystemTool` abstract interface

2. **Application Layer** (`server/application/tool_handlers/system_handler.py`)
   - `SystemToolHandler` implementing RPC bridge

3. **Adapter Layer** (`server/adapters/mcp/areas/system.py`)
   - MCP tool definitions with semantic tags

4. **Blender Addon** (`blender_addon/application/handlers/system.py`)
   - `SystemHandler` with actual bpy implementation

### Key Features

- **Mode switching with object selection**: `system_set_mode` can optionally set active object before mode switch
- **Safe undo/redo**: Limited to 10 steps per call, handles edge cases gracefully
- **Smart file saving**: Auto-generates temp paths for unsaved files
- **Snapshot system**: Lightweight .blend checkpoints in temp directory

---

## Testing

- **36 new unit tests** covering all system handler functionality
- **E2E tests** prepared for live Blender testing

---

## Files Changed

### New Files
- `server/domain/tools/system.py`
- `server/application/tool_handlers/system_handler.py`
- `server/adapters/mcp/areas/system.py`
- `blender_addon/application/handlers/system.py`
- `tests/unit/tools/system/__init__.py`
- `tests/unit/tools/system/test_system_handler.py`
- `tests/e2e/tools/system/__init__.py`
- `tests/e2e/tools/system/test_system_tools.py`

### Modified Files
- `server/adapters/mcp/areas/__init__.py` - Added system import
- `server/infrastructure/di.py` - Added `get_system_handler()`
- `blender_addon/__init__.py` - Added SystemHandler registration
