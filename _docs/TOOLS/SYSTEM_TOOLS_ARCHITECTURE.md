# System Tools Architecture

> **TASK-025 Implementation** | Version 1.20.0

---

## Overview

System Tools provide low-level operations for mode switching, undo/redo, file management, and checkpoint management. These tools are essential for AI-driven workflows that need to manage Blender's state reliably.

---

## Tool Summary

| Tool | Description | Tags |
|------|-------------|------|
| `system_set_mode` | Switches Blender mode with optional object selection | `[SCENE][SAFE]` |
| `system_undo` | Undoes last operation(s), max 10 steps | `[SCENE][NON-DESTRUCTIVE]` |
| `system_redo` | Redoes previously undone operation(s), max 10 steps | `[SCENE][NON-DESTRUCTIVE]` |
| `system_save_file` | Saves current .blend file | `[SCENE][DESTRUCTIVE]` |
| `system_new_file` | Creates new file (resets scene) | `[SCENE][DESTRUCTIVE]` |
| `system_snapshot` | Manages quick save/restore checkpoints | `[SCENE][NON-DESTRUCTIVE]` |

---

## Architecture (4 Layers)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. DOMAIN LAYER                                             │
│    server/domain/tools/system.py                            │
│    - ISystemTool abstract interface                         │
│    - Method signatures for all system operations            │
├─────────────────────────────────────────────────────────────┤
│ 2. APPLICATION LAYER (RPC Bridge)                           │
│    server/application/tool_handlers/system_handler.py       │
│    - SystemToolHandler implements ISystemTool               │
│    - Sends RPC requests to Blender addon                    │
├─────────────────────────────────────────────────────────────┤
│ 3. ADAPTER LAYER (MCP Definition)                           │
│    server/adapters/mcp/areas/system.py                      │
│    - @mcp.tool() decorated functions                        │
│    - Semantic tags in docstrings                            │
│    - Parameter validation and conversion                    │
├─────────────────────────────────────────────────────────────┤
│ 4. BLENDER ADDON (Execution)                                │
│    blender_addon/application/handlers/system.py             │
│    - SystemHandler with actual bpy implementation           │
│    - RPC handler registration in __init__.py                │
└─────────────────────────────────────────────────────────────┘
```

---

## Tool Details

### `system_set_mode`

**Purpose:** Switches Blender interaction mode (OBJECT, EDIT, SCULPT, POSE, etc.) with optional object selection.

**Signature:**
```python
system_set_mode(mode: str, object_name: Optional[str] = None) -> str
```

**Arguments:**
| Arg | Type | Required | Description |
|-----|------|----------|-------------|
| `mode` | str | Yes | Target mode (OBJECT, EDIT, SCULPT, POSE, VERTEX_PAINT, WEIGHT_PAINT, TEXTURE_PAINT) |
| `object_name` | str | No | Object to make active before switching mode |

**Mode Validation by Object Type:**
| Object Type | Allowed Modes |
|-------------|---------------|
| MESH | OBJECT, EDIT, SCULPT, VERTEX_PAINT, WEIGHT_PAINT, TEXTURE_PAINT |
| ARMATURE | OBJECT, EDIT, POSE |
| CURVE, SURFACE, FONT | OBJECT, EDIT |
| LATTICE | OBJECT, EDIT |
| META | OBJECT, EDIT |
| GREASE_PENCIL | OBJECT, EDIT, SCULPT, VERTEX_PAINT, WEIGHT_PAINT |
| Others | OBJECT only |

**Example:**
```python
# Enter Edit Mode on a specific object
system_set_mode(mode="EDIT", object_name="Cube")

# Switch to Sculpt Mode (uses current active object)
system_set_mode(mode="SCULPT")
```

---

### `system_undo`

**Purpose:** Undoes the last operation(s). Safe for AI workflows with step limit.

**Signature:**
```python
system_undo(steps: int = 1) -> str
```

**Arguments:**
| Arg | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| `steps` | int | No | 1 | Number of undo steps (max 10) |

**Safety Features:**
- Maximum 10 steps per call to prevent runaway undos
- Graceful handling when undo history is exhausted
- Returns descriptive message about undone operations

**Undo Granularity (Addon):**
- Undo granularity depends on Blender’s internal undo stack.
- The Blender addon best-effort inserts an undo boundary after successful **mutating** MCP/RPC commands to keep `system_undo(steps=1)` closer to “undo the last tool call”.
- To disable automatic undo boundaries, set `BLENDER_AI_MCP_AUTO_UNDO_PUSH=0` before starting Blender.

**Example:**
```python
# Undo last operation
system_undo()

# Undo last 5 operations
system_undo(steps=5)
```

---

### `system_redo`

**Purpose:** Redoes previously undone operation(s).

**Signature:**
```python
system_redo(steps: int = 1) -> str
```

**Arguments:**
| Arg | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| `steps` | int | No | 1 | Number of redo steps (max 10) |

**Safety Features:**
- Maximum 10 steps per call
- Graceful handling when redo history is exhausted

---

### `system_save_file`

**Purpose:** Saves the current .blend file. Auto-generates temp path for unsaved files.

**Signature:**
```python
system_save_file(filepath: Optional[str] = None, compress: bool = True) -> str
```

**Arguments:**
| Arg | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| `filepath` | str | No | None | Target path (uses current if None, generates temp if unsaved) |
| `compress` | bool | No | True | Use compression for smaller file size |

**Behavior:**
- If `filepath` provided: Saves to that path
- If no `filepath` and file has been saved: Saves to current path
- If no `filepath` and file is untitled: Generates temp path in system temp directory

**Example:**
```python
# Save to current location
system_save_file()

# Save to specific path
system_save_file(filepath="/path/to/my_scene.blend")

# Save without compression
system_save_file(compress=False)
```

---

### `system_new_file`

**Purpose:** Creates a new file (resets scene to startup state).

**Signature:**
```python
system_new_file(load_ui: bool = False) -> str
```

**Arguments:**
| Arg | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| `load_ui` | bool | No | False | Whether to load UI settings from startup file |

**Warning:** This is a destructive operation that clears all unsaved work.

---

### `system_snapshot`

**Purpose:** Manages lightweight .blend checkpoints in temp directory for quick save/restore.

**Signature:**
```python
system_snapshot(action: str, name: Optional[str] = None) -> str
```

**Arguments:**
| Arg | Type | Required | Description |
|-----|------|----------|-------------|
| `action` | str | Yes | Operation: `save`, `restore`, `list`, `delete` |
| `name` | str | Conditional | Snapshot name (required for save/restore/delete) |

**Actions:**
| Action | Name Required | Description |
|--------|---------------|-------------|
| `save` | Yes | Creates snapshot with given name |
| `restore` | Yes | Restores from snapshot with given name |
| `list` | No | Lists all available snapshots |
| `delete` | Yes | Deletes snapshot with given name |

**Storage:**
- Snapshots are stored in system temp directory as `.blend` files
- Path pattern: `{temp_dir}/blender_snapshot_{name}.blend`

**Example:**
```python
# Save checkpoint before risky operation
system_snapshot(action="save", name="before_boolean")

# List available snapshots
system_snapshot(action="list")

# Restore if something went wrong
system_snapshot(action="restore", name="before_boolean")

# Clean up old snapshot
system_snapshot(action="delete", name="before_boolean")
```

---

## AI Workflow Patterns

### Safe Experimentation Pattern
```
1. system_snapshot(action="save", name="checkpoint")
2. <risky operations>
3. If failed: system_snapshot(action="restore", name="checkpoint")
4. system_snapshot(action="delete", name="checkpoint")
```

### Mode-Aware Operations
```
1. scene_context(action="mode") -> Check current mode
2. system_set_mode(mode="EDIT", object_name="MyMesh")
3. <Edit Mode operations>
4. system_set_mode(mode="OBJECT")
```

### Undo-Based Recovery
```
1. <operation that might fail>
2. If result unsatisfactory: system_undo(steps=1)
3. Try alternative approach
```

---

## Testing

### Unit Tests
Location: `tests/unit/tools/system/test_system_handler.py`

**Test Coverage:**
- `TestSystemSetMode`: Mode validation by object type, object selection
- `TestSystemUndoRedo`: Step limits, edge cases
- `TestSystemSaveFile`: Path handling, compression
- `TestSystemNewFile`: UI loading options
- `TestSystemSnapshot`: All actions (save/restore/list/delete)

**Total:** 36 unit tests

### E2E Tests
Location: `tests/e2e/tools/system/test_system_tools.py`

Tests require live Blender with addon enabled.

---

## Files

| Layer | File |
|-------|------|
| Domain | `server/domain/tools/system.py` |
| Application | `server/application/tool_handlers/system_handler.py` |
| Adapter | `server/adapters/mcp/areas/system.py` |
| Addon | `blender_addon/application/handlers/system.py` |
| Unit Tests | `tests/unit/tools/system/test_system_handler.py` |
| E2E Tests | `tests/e2e/tools/system/test_system_tools.py` |
