"""Export handler for file export operations in Blender."""

import os

import bpy


class ExportHandler:
    """Application service for file export operations."""

    def export_glb(
        self,
        filepath: str,
        export_selected: bool = False,
        export_animations: bool = True,
        export_materials: bool = True,
        apply_modifiers: bool = True,
    ) -> str:
        """Exports scene or selected objects to GLB/GLTF format.

        Args:
            filepath: Output file path
            export_selected: Export only selected objects
            export_animations: Include animations
            export_materials: Include materials and textures
            apply_modifiers: Apply modifiers before export

        Returns:
            Success message with file path
        """
        # Ensure correct extension
        if not filepath.lower().endswith((".glb", ".gltf")):
            filepath += ".glb"

        # Ensure directory exists
        dir_path = os.path.dirname(filepath)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        # Determine export format
        export_format = "GLB" if filepath.lower().endswith(".glb") else "GLTF_SEPARATE"

        # Export with GLTF exporter
        bpy.ops.export_scene.gltf(
            filepath=filepath,
            export_format=export_format,
            use_selection=export_selected,
            export_animations=export_animations,
            export_materials="EXPORT" if export_materials else "NONE",
            export_apply=apply_modifiers,
        )

        return f"Successfully exported to '{filepath}'"

    def export_fbx(
        self,
        filepath: str,
        export_selected: bool = False,
        export_animations: bool = True,
        apply_modifiers: bool = True,
        mesh_smooth_type: str = "FACE",
    ) -> str:
        """Exports scene or selected objects to FBX format.

        Args:
            filepath: Output file path
            export_selected: Export only selected objects
            export_animations: Include animations and armature
            apply_modifiers: Apply modifiers before export
            mesh_smooth_type: Smoothing export method ('OFF', 'FACE', 'EDGE')

        Returns:
            Success message with file path
        """
        # Ensure correct extension
        if not filepath.lower().endswith(".fbx"):
            filepath += ".fbx"

        # Ensure directory exists
        dir_path = os.path.dirname(filepath)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        # Validate mesh_smooth_type
        valid_smooth_types = {"OFF", "FACE", "EDGE"}
        if mesh_smooth_type not in valid_smooth_types:
            mesh_smooth_type = "FACE"

        # Export with FBX exporter
        bpy.ops.export_scene.fbx(
            filepath=filepath,
            use_selection=export_selected,
            bake_anim=export_animations,
            use_mesh_modifiers=apply_modifiers,
            mesh_smooth_type=mesh_smooth_type,
            add_leaf_bones=False,
            primary_bone_axis="Y",
            secondary_bone_axis="X",
        )

        return f"Successfully exported to '{filepath}'"

    def export_obj(
        self,
        filepath: str,
        export_selected: bool = False,
        apply_modifiers: bool = True,
        export_materials: bool = True,
        export_uvs: bool = True,
        export_normals: bool = True,
        triangulate: bool = False,
    ) -> str:
        """Exports scene or selected objects to OBJ format.

        Args:
            filepath: Output file path
            export_selected: Export only selected objects
            apply_modifiers: Apply modifiers before export
            export_materials: Export .mtl material file
            export_uvs: Include UV coordinates
            export_normals: Include vertex normals
            triangulate: Convert quads/ngons to triangles

        Returns:
            Success message with file path
        """
        # Ensure correct extension
        if not filepath.lower().endswith(".obj"):
            filepath += ".obj"

        # Ensure directory exists
        dir_path = os.path.dirname(filepath)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        # Export with OBJ exporter (Blender 3.3+ uses wm.obj_export)
        bpy.ops.wm.obj_export(
            filepath=filepath,
            export_selected_objects=export_selected,
            apply_modifiers=apply_modifiers,
            export_materials=export_materials,
            export_uv=export_uvs,
            export_normals=export_normals,
            export_triangulated_mesh=triangulate,
        )

        return f"Successfully exported to '{filepath}'"
