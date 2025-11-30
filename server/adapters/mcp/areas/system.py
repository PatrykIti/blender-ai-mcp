from typing import Literal, Optional
from fastmcp import Context
from server.adapters.mcp.instance import mcp
from server.infrastructure.di import get_system_handler


# === Export Tools ===


@mcp.tool()
def export_glb(
    ctx: Context,
    filepath: str,
    export_selected: bool = False,
    export_animations: bool = True,
    export_materials: bool = True,
    apply_modifiers: bool = True,
) -> str:
    """
    [OBJECT MODE][SCENE][SAFE] Exports scene or selected objects to GLB/GLTF format.

    GLB is the binary variant of GLTF - ideal for web, game engines (Unity, Unreal, Godot).
    Supports PBR materials, animations, and skeletal rigs.

    Workflow: BEFORE -> scene_list_objects (verify objects) | AFTER -> file ready for import

    Args:
        filepath: Output file path (must end with .glb or .gltf)
        export_selected: Export only selected objects (default: entire scene)
        export_animations: Include animations
        export_materials: Include materials and textures
        apply_modifiers: Apply modifiers before export
    """
    handler = get_system_handler()
    try:
        result = handler.export_glb(
            filepath=filepath,
            export_selected=export_selected,
            export_animations=export_animations,
            export_materials=export_materials,
            apply_modifiers=apply_modifiers,
        )
        ctx.info(f"Exported GLB to: {filepath}")
        return result
    except RuntimeError as e:
        return str(e)


@mcp.tool()
def export_fbx(
    ctx: Context,
    filepath: str,
    export_selected: bool = False,
    export_animations: bool = True,
    apply_modifiers: bool = True,
    mesh_smooth_type: Literal["OFF", "FACE", "EDGE"] = "FACE",
) -> str:
    """
    [OBJECT MODE][SCENE][SAFE] Exports scene or selected objects to FBX format.

    FBX is the industry standard for game engines and DCC interchange.
    Supports animations, armatures, blend shapes, and materials.

    Workflow: BEFORE -> scene_list_objects (verify objects) | AFTER -> file ready for import

    Args:
        filepath: Output file path (must end with .fbx)
        export_selected: Export only selected objects
        export_animations: Include animations and armature
        apply_modifiers: Apply modifiers before export
        mesh_smooth_type: Smoothing export method (OFF, FACE, EDGE)
    """
    handler = get_system_handler()
    try:
        result = handler.export_fbx(
            filepath=filepath,
            export_selected=export_selected,
            export_animations=export_animations,
            apply_modifiers=apply_modifiers,
            mesh_smooth_type=mesh_smooth_type,
        )
        ctx.info(f"Exported FBX to: {filepath}")
        return result
    except RuntimeError as e:
        return str(e)


@mcp.tool()
def export_obj(
    ctx: Context,
    filepath: str,
    export_selected: bool = False,
    apply_modifiers: bool = True,
    export_materials: bool = True,
    export_uvs: bool = True,
    export_normals: bool = True,
    triangulate: bool = False,
) -> str:
    """
    [OBJECT MODE][SCENE][SAFE] Exports scene or selected objects to OBJ format.

    OBJ is a simple, universal mesh format supported by virtually all 3D software.
    Creates .obj (geometry) and optionally .mtl (materials) files.

    Workflow: BEFORE -> scene_list_objects (verify objects) | AFTER -> file ready for import

    Args:
        filepath: Output file path (must end with .obj)
        export_selected: Export only selected objects
        apply_modifiers: Apply modifiers before export
        export_materials: Export .mtl material file
        export_uvs: Include UV coordinates
        export_normals: Include vertex normals
        triangulate: Convert quads/ngons to triangles
    """
    handler = get_system_handler()
    try:
        result = handler.export_obj(
            filepath=filepath,
            export_selected=export_selected,
            apply_modifiers=apply_modifiers,
            export_materials=export_materials,
            export_uvs=export_uvs,
            export_normals=export_normals,
            triangulate=triangulate,
        )
        ctx.info(f"Exported OBJ to: {filepath}")
        return result
    except RuntimeError as e:
        return str(e)


# === Import Tools ===


@mcp.tool()
def import_obj(
    ctx: Context,
    filepath: str,
    use_split_objects: bool = True,
    use_split_groups: bool = False,
    global_scale: float = 1.0,
    forward_axis: Literal["NEGATIVE_Z", "Z", "NEGATIVE_Y", "Y", "NEGATIVE_X", "X"] = "NEGATIVE_Z",
    up_axis: Literal["Y", "Z", "X"] = "Y",
) -> str:
    """
    [OBJECT MODE][SCENE] Imports OBJ file into the scene.

    OBJ is the most universal 3D format - supported by virtually all 3D software.
    Imports geometry, UVs, normals, and optionally materials from .mtl file.

    Workflow: AFTER -> mesh_tris_to_quads (if triangulated) | mesh_normals_make_consistent

    Args:
        filepath: Path to OBJ file (must exist on Blender host)
        use_split_objects: Split by object - creates separate Blender objects (default: True)
        use_split_groups: Split by group names
        global_scale: Scale factor for imported geometry (1.0 = original size)
        forward_axis: Forward axis in Blender (NEGATIVE_Z = -Z forward, standard for most apps)
        up_axis: Up axis in Blender (Y = Y-up standard)
    """
    handler = get_system_handler()
    try:
        result = handler.import_obj(
            filepath=filepath,
            use_split_objects=use_split_objects,
            use_split_groups=use_split_groups,
            global_scale=global_scale,
            forward_axis=forward_axis,
            up_axis=up_axis,
        )
        ctx.info(f"Imported OBJ from: {filepath}")
        return result
    except RuntimeError as e:
        return str(e)


@mcp.tool()
def import_fbx(
    ctx: Context,
    filepath: str,
    use_custom_normals: bool = True,
    use_image_search: bool = True,
    ignore_leaf_bones: bool = False,
    automatic_bone_orientation: bool = False,
    global_scale: float = 1.0,
) -> str:
    """
    [OBJECT MODE][SCENE] Imports FBX file into the scene.

    FBX is the industry standard for game engines (Unity, Unreal).
    Supports geometry, materials, animations, armatures, and blend shapes.

    Workflow: AFTER -> scene_list_objects (verify imported objects)

    Args:
        filepath: Path to FBX file (must exist on Blender host)
        use_custom_normals: Use custom normals from file (preserves author's normals)
        use_image_search: Search for texture images in file path
        ignore_leaf_bones: Ignore leaf bones (tip bones) - cleaner armature import
        automatic_bone_orientation: Auto-orient bones to Blender conventions
        global_scale: Scale factor for imported geometry (1.0 = original size)
    """
    handler = get_system_handler()
    try:
        result = handler.import_fbx(
            filepath=filepath,
            use_custom_normals=use_custom_normals,
            use_image_search=use_image_search,
            ignore_leaf_bones=ignore_leaf_bones,
            automatic_bone_orientation=automatic_bone_orientation,
            global_scale=global_scale,
        )
        ctx.info(f"Imported FBX from: {filepath}")
        return result
    except RuntimeError as e:
        return str(e)


@mcp.tool()
def import_glb(
    ctx: Context,
    filepath: str,
    import_pack_images: bool = True,
    merge_vertices: bool = False,
    import_shading: Literal["NORMALS", "FLAT", "SMOOTH"] = "NORMALS",
) -> str:
    """
    [OBJECT MODE][SCENE] Imports GLB/GLTF file into the scene.

    GLTF is the modern web/game format - supports PBR materials, animations, and more.
    GLB is the binary variant (single file with embedded textures).

    Workflow: AFTER -> scene_list_objects (verify imported objects)

    Args:
        filepath: Path to GLB/GLTF file (must exist on Blender host)
        import_pack_images: Pack images into .blend file (keeps textures internal)
        merge_vertices: Merge duplicate vertices (may break UV seams)
        import_shading: How to handle shading (NORMALS = use file normals, FLAT, SMOOTH)
    """
    handler = get_system_handler()
    try:
        result = handler.import_glb(
            filepath=filepath,
            import_pack_images=import_pack_images,
            merge_vertices=merge_vertices,
            import_shading=import_shading,
        )
        ctx.info(f"Imported GLB/GLTF from: {filepath}")
        return result
    except RuntimeError as e:
        return str(e)


@mcp.tool()
def import_image_as_plane(
    ctx: Context,
    filepath: str,
    name: Optional[str] = None,
    location: Optional[list] = None,
    size: float = 1.0,
    align_axis: Literal["Z+", "Y+", "X+", "Z-", "Y-", "X-"] = "Z+",
    shader: Literal["PRINCIPLED", "SHADELESS", "EMISSION"] = "PRINCIPLED",
    use_transparency: bool = True,
) -> str:
    """
    [OBJECT MODE][SCENE] Imports image file as a textured plane.

    Perfect for:
    - Reference images (blueprints, concept art)
    - Background plates for compositing
    - Decals and signage
    - Quick texturing

    Workflow: Use as reference for modeling | Adjust plane transform as needed

    Args:
        filepath: Path to image file (PNG, JPG, etc. - must exist on Blender host)
        name: Optional name for the created plane (defaults to filename)
        location: Optional [x, y, z] location for the plane
        size: Scale of the plane relative to image aspect ratio
        align_axis: Which axis the plane faces (Z+ = facing up, Y+ = facing front)
        shader: Material shader type (PRINCIPLED = PBR, SHADELESS = unlit, EMISSION = glowing)
        use_transparency: Use alpha channel for transparency (PNG with alpha)
    """
    handler = get_system_handler()
    try:
        result = handler.import_image_as_plane(
            filepath=filepath,
            name=name,
            location=location,
            size=size,
            align_axis=align_axis,
            shader=shader,
            use_transparency=use_transparency,
        )
        ctx.info(f"Imported image as plane from: {filepath}")
        return result
    except RuntimeError as e:
        return str(e)


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
