from typing import Literal

from fastmcp import Context

from server.adapters.mcp.instance import mcp
from server.infrastructure.di import get_import_handler


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
    handler = get_import_handler()
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
    handler = get_import_handler()
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
    handler = get_import_handler()
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
    name: str | None = None,
    location: list[float] | None = None,
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
    handler = get_import_handler()
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
