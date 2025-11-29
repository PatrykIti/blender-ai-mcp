from typing import Literal

from fastmcp import Context

from server.adapters.mcp.instance import mcp
from server.infrastructure.di import get_export_handler


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
    handler = get_export_handler()
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
    handler = get_export_handler()
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
    handler = get_export_handler()
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
