from typing import Literal, Optional
from fastmcp import Context
from server.adapters.mcp.instance import mcp
from server.infrastructure.di import get_system_handler


@mcp.tool()
def system_set_mode(
    ctx: Context,
    mode: Literal["OBJECT", "EDIT", "SCULPT", "VERTEX_PAINT", "WEIGHT_PAINT", "TEXTURE_PAINT", "POSE"],
    object_name: Optional[str] = None,
) -> str:
    """
    [SCENE][SAFE] Switches Blender mode for the active or specified object.

    Modes:
        - OBJECT: Object manipulation mode
        - EDIT: Geometry editing mode (MESH, CURVE, SURFACE, META, FONT, LATTICE, ARMATURE)
        - SCULPT: Sculpting mode (MESH only)
        - VERTEX_PAINT: Vertex color painting (MESH only)
        - WEIGHT_PAINT: Vertex weight painting (MESH only)
        - TEXTURE_PAINT: Texture painting mode (MESH only)
        - POSE: Armature pose mode (ARMATURE only)

    Workflow: CRITICAL -> switching OBJECT<->EDIT | BEFORE -> mesh_* or modeling_*

    Args:
        mode: Target mode
        object_name: Object to set mode for (default: active object). If provided,
                    the object will be set as active before mode switch.
    """
    handler = get_system_handler()
    try:
        return handler.set_mode(mode, object_name)
    except RuntimeError as e:
        return str(e)


@mcp.tool()
def system_undo(ctx: Context, steps: int = 1) -> str:
    """
    [SCENE][NON-DESTRUCTIVE] Undoes the last operation(s).

    Safe way to revert changes during AI-assisted modeling sessions.
    Limited to 10 steps per call for safety.

    Workflow: ERROR RECOVERY -> undo mistakes | AFTER -> any destructive operation

    Args:
        steps: Number of steps to undo (default: 1, max: 10)
    """
    handler = get_system_handler()
    try:
        return handler.undo(steps)
    except RuntimeError as e:
        return str(e)


@mcp.tool()
def system_redo(ctx: Context, steps: int = 1) -> str:
    """
    [SCENE][NON-DESTRUCTIVE] Redoes previously undone operation(s).

    Restores changes that were previously undone.
    Limited to 10 steps per call for safety.

    Workflow: AFTER -> system_undo | RESTORE -> previous state

    Args:
        steps: Number of steps to redo (default: 1, max: 10)
    """
    handler = get_system_handler()
    try:
        return handler.redo(steps)
    except RuntimeError as e:
        return str(e)


@mcp.tool()
def system_save_file(
    ctx: Context,
    filepath: Optional[str] = None,
    compress: bool = True,
) -> str:
    """
    [SCENE][DESTRUCTIVE] Saves the current Blender file.

    If no filepath is provided:
    - Saves to current file path if file was previously saved
    - Creates auto-save in temp directory if file is unsaved

    WARNING: Overwrites existing file at filepath!

    Workflow: CHECKPOINT -> save progress | BEFORE -> risky operations

    Args:
        filepath: Path to save (default: current file path, or temp if unsaved)
        compress: Compress .blend file (default: True)
    """
    handler = get_system_handler()
    try:
        return handler.save_file(filepath, compress)
    except RuntimeError as e:
        return str(e)


@mcp.tool()
def system_new_file(ctx: Context, load_ui: bool = False) -> str:
    """
    [SCENE][DESTRUCTIVE] Creates a new Blender file (clears current scene).

    WARNING: Unsaved changes will be lost! Use system_save_file first if needed.

    Workflow: START FRESH -> new project | AFTER -> system_save_file

    Args:
        load_ui: Load UI layout from startup file (default: False)
    """
    handler = get_system_handler()
    try:
        return handler.new_file(load_ui)
    except RuntimeError as e:
        return str(e)


@mcp.tool()
def system_snapshot(
    ctx: Context,
    action: Literal["save", "restore", "list", "delete"],
    name: Optional[str] = None,
) -> str:
    """
    [SCENE][NON-DESTRUCTIVE] Manages quick save/restore checkpoints.

    Snapshots are lightweight .blend file copies stored in a temp directory.
    They persist until Blender restarts or system temp is cleaned.

    Actions:
        - save: Save current state with name (auto-generates timestamp if name not provided)
        - restore: Restore to named snapshot (name required)
        - list: List all available snapshots
        - delete: Delete named snapshot (name required)

    Use Cases:
        - Before risky operations: system_snapshot(action="save", name="before_boolean")
        - Quick iteration: save -> experiment -> restore if unhappy
        - Compare states: save multiple snapshots with descriptive names

    Workflow: CHECKPOINT -> quick save | BEFORE -> experimental operations

    Args:
        action: Operation to perform
        name: Snapshot name (required for restore/delete, optional for save)
    """
    handler = get_system_handler()
    try:
        return handler.snapshot(action, name)
    except RuntimeError as e:
        return str(e)
