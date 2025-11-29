# TASK-025: System Tools

**Status:** To Do
**Priority:** 🟡 Medium
**Category:** System Tools

---

## Overview

Implement system-level tools for mode switching, undo/redo, and file operations.

---

# TASK-025-1: system_set_mode

**Status:** To Do
**Priority:** 🟡 Medium

## Objective

Implement `system_set_mode` as high-level mode switching tool.

## Architecture Requirements

### 1. Domain Layer (`server/domain/tools/system.py`)

Create new domain interface:

```python
from abc import ABC, abstractmethod

class ISystemTool(ABC):
    @abstractmethod
    def set_mode(
        self,
        mode: str,  # 'OBJECT', 'EDIT', 'SCULPT', 'VERTEX_PAINT', 'WEIGHT_PAINT', 'TEXTURE_PAINT'
        object_name: str = None,
    ) -> str:
        pass
```

### 2. Application Layer (`server/application/tool_handlers/system_handler.py`)

Create `SystemToolHandler`:

```python
from server.domain.tools.system import ISystemTool
from server.domain.interfaces.rpc_client import IRpcClient

class SystemToolHandler(ISystemTool):
    def __init__(self, rpc_client: IRpcClient):
        self.rpc = rpc_client

    def set_mode(self, mode: str, object_name: str = None) -> str:
        return self.rpc.send_request("system.set_mode", {
            "mode": mode,
            "object_name": object_name
        })
```

### 3. Adapter Layer (`server/adapters/mcp/areas/system.py`)

```python
@mcp.tool()
def system_set_mode(
    ctx: Context,
    mode: Literal["OBJECT", "EDIT", "SCULPT", "VERTEX_PAINT", "WEIGHT_PAINT", "TEXTURE_PAINT"],
    object_name: str = None,
) -> str:
    """
    [SCENE][SAFE] Switches Blender mode for the active or specified object.

    Modes:
        - OBJECT: Object manipulation mode
        - EDIT: Geometry editing mode
        - SCULPT: Sculpting mode
        - VERTEX_PAINT: Vertex color painting
        - WEIGHT_PAINT: Vertex weight painting
        - TEXTURE_PAINT: Texture painting mode

    Args:
        mode: Target mode
        object_name: Object to set mode for (default: active object)
    """
```

### 4. Blender Addon (`blender_addon/application/handlers/system.py`)

Create `SystemHandler`:

```python
import bpy

class SystemHandler:
    def set_mode(self, mode, object_name=None):
        if object_name:
            obj = bpy.data.objects.get(object_name)
            if not obj:
                return f"Object '{object_name}' not found"
            bpy.context.view_layer.objects.active = obj

        obj = bpy.context.active_object
        if not obj:
            return "No active object"

        # Check if mode is valid for object type
        if mode in ['EDIT', 'SCULPT'] and obj.type != 'MESH':
            return f"Mode '{mode}' not available for object type '{obj.type}'"

        bpy.ops.object.mode_set(mode=mode)
        return f"Set mode to {mode} for '{obj.name}'"
```

### 5. Infrastructure & Registration

- Add `get_system_handler()` to `server/infrastructure/di.py`
- Register RPC handler in `blender_addon/__init__.py`

## Deliverables

- [ ] New System domain
- [ ] Application handler
- [ ] MCP adapter
- [ ] Blender addon handler
- [ ] Unit tests
- [ ] Documentation

---

# TASK-025-2: system_undo / system_redo

**Status:** To Do
**Priority:** 🟡 Medium

## Objective

Implement safe undo/redo operations for AI workflows.

## Architecture Requirements

### 1. Domain Layer

```python
@abstractmethod
def undo(self, steps: int = 1) -> str:
    pass

@abstractmethod
def redo(self, steps: int = 1) -> str:
    pass
```

### 2. Adapter Layer

```python
@mcp.tool()
def system_undo(ctx: Context, steps: int = 1) -> str:
    """
    [SCENE][NON-DESTRUCTIVE] Undoes the last operation(s).

    Args:
        steps: Number of steps to undo (default: 1, max: 10)
    """

@mcp.tool()
def system_redo(ctx: Context, steps: int = 1) -> str:
    """
    [SCENE][NON-DESTRUCTIVE] Redoes previously undone operation(s).

    Args:
        steps: Number of steps to redo (default: 1, max: 10)
    """
```

### 3. Blender Addon

```python
def undo(self, steps=1):
    steps = min(steps, 10)  # Safety limit
    for _ in range(steps):
        bpy.ops.ed.undo()
    return f"Undone {steps} step(s)"

def redo(self, steps=1):
    steps = min(steps, 10)  # Safety limit
    for _ in range(steps):
        bpy.ops.ed.redo()
    return f"Redone {steps} step(s)"
```

## Deliverables

- [ ] Implementation + Tests
- [ ] Documentation

---

# TASK-025-3: system_save_file / system_new_file

**Status:** To Do
**Priority:** 🟡 Medium

## Objective

Implement file save and new file operations.

## Architecture Requirements

### 1. Domain Layer

```python
@abstractmethod
def save_file(self, filepath: str = None, compress: bool = True) -> str:
    pass

@abstractmethod
def new_file(self, load_ui: bool = False) -> str:
    pass
```

### 2. Adapter Layer

```python
@mcp.tool()
def system_save_file(
    ctx: Context,
    filepath: str = None,
    compress: bool = True,
) -> str:
    """
    [SCENE][DESTRUCTIVE] Saves the current Blender file.

    Args:
        filepath: Path to save (default: current file path, or temp if unsaved)
        compress: Compress .blend file (default: True)
    """

@mcp.tool()
def system_new_file(ctx: Context, load_ui: bool = False) -> str:
    """
    [SCENE][DESTRUCTIVE] Creates a new Blender file (clears current scene).

    WARNING: Unsaved changes will be lost!

    Args:
        load_ui: Load UI from startup file
    """
```

### 3. Blender Addon

```python
def save_file(self, filepath=None, compress=True):
    if filepath:
        bpy.ops.wm.save_as_mainfile(filepath=filepath, compress=compress)
        return f"Saved file to '{filepath}'"
    else:
        if bpy.data.filepath:
            bpy.ops.wm.save_mainfile(compress=compress)
            return f"Saved file '{bpy.data.filepath}'"
        else:
            # Generate temp path
            import tempfile
            import os
            filepath = os.path.join(tempfile.gettempdir(), "blender_ai_autosave.blend")
            bpy.ops.wm.save_as_mainfile(filepath=filepath, compress=compress)
            return f"Saved file to '{filepath}'"

def new_file(self, load_ui=False):
    bpy.ops.wm.read_homefile(load_ui=load_ui)
    return "Created new file"
```

## Deliverables

- [ ] Implementation + Tests
- [ ] Documentation

---

# TASK-025-4: system_snapshot

**Status:** To Do
**Priority:** 🟢 Low

## Objective

Implement quick save/restore checkpoints for complex modeling sessions.

## Architecture Requirements

### 1. Domain Layer

```python
@abstractmethod
def snapshot(
    self,
    action: str,  # 'save', 'restore', 'list', 'delete'
    name: str = None,
) -> str:
    pass
```

### 2. Adapter Layer

```python
@mcp.tool()
def system_snapshot(
    ctx: Context,
    action: Literal["save", "restore", "list", "delete"],
    name: str = None,
) -> str:
    """
    [SCENE][NON-DESTRUCTIVE] Manages quick save/restore checkpoints.

    Actions:
        - save: Save current state with name (or auto-generated timestamp)
        - restore: Restore to named snapshot
        - list: List all available snapshots
        - delete: Delete named snapshot

    Snapshots are stored in temp directory and cleared on Blender restart.

    Args:
        action: Operation to perform
        name: Snapshot name (required for restore/delete)
    """
```

### 3. Blender Addon

```python
import os
import tempfile
from datetime import datetime

class SystemHandler:
    SNAPSHOT_DIR = os.path.join(tempfile.gettempdir(), "blender_ai_snapshots")

    def snapshot(self, action, name=None):
        os.makedirs(self.SNAPSHOT_DIR, exist_ok=True)

        if action == "save":
            name = name or datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(self.SNAPSHOT_DIR, f"{name}.blend")
            bpy.ops.wm.save_as_mainfile(filepath=filepath, copy=True)
            return f"Saved snapshot '{name}'"

        elif action == "restore":
            if not name:
                return "Snapshot name required for restore"
            filepath = os.path.join(self.SNAPSHOT_DIR, f"{name}.blend")
            if not os.path.exists(filepath):
                return f"Snapshot '{name}' not found"
            bpy.ops.wm.open_mainfile(filepath=filepath)
            return f"Restored snapshot '{name}'"

        elif action == "list":
            files = [f[:-6] for f in os.listdir(self.SNAPSHOT_DIR) if f.endswith('.blend')]
            return f"Snapshots: {', '.join(files) or '(none)'}"

        elif action == "delete":
            if not name:
                return "Snapshot name required for delete"
            filepath = os.path.join(self.SNAPSHOT_DIR, f"{name}.blend")
            if os.path.exists(filepath):
                os.remove(filepath)
                return f"Deleted snapshot '{name}'"
            return f"Snapshot '{name}' not found"
```

## Deliverables

- [ ] Implementation + Tests
- [ ] Documentation

---

## Summary

| Tool | Priority | Description |
|------|----------|-------------|
| `system_set_mode` | 🟡 Medium | High-level mode switching |
| `system_undo` | 🟡 Medium | Safe undo for AI |
| `system_redo` | 🟡 Medium | Safe redo for AI |
| `system_save_file` | 🟡 Medium | Save .blend file |
| `system_new_file` | 🟡 Medium | Create new file |
| `system_snapshot` | 🟢 Low | Quick save/restore checkpoints |
