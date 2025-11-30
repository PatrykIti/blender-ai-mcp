"""Import handler for file import operations in Blender."""

import os

import bpy


class ImportHandler:
    """Application service for file import operations."""

    def import_obj(
        self,
        filepath: str,
        use_split_objects: bool = True,
        use_split_groups: bool = False,
        global_scale: float = 1.0,
        forward_axis: str = "NEGATIVE_Z",
        up_axis: str = "Y",
    ) -> str:
        """Imports OBJ file.

        Args:
            filepath: Path to OBJ file
            use_split_objects: Split by object
            use_split_groups: Split by groups
            global_scale: Scale factor
            forward_axis: Forward axis
            up_axis: Up axis

        Returns:
            Success message with imported object names
        """
        # Validate file exists
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"OBJ file not found: {filepath}")

        # Track objects before import
        objects_before = set(bpy.data.objects.keys())

        # Import OBJ (Blender 3.3+ uses wm.obj_import)
        bpy.ops.wm.obj_import(
            filepath=filepath,
            use_split_objects=use_split_objects,
            use_split_groups=use_split_groups,
            global_scale=global_scale,
            forward_axis=forward_axis,
            up_axis=up_axis,
        )

        # Find newly imported objects
        objects_after = set(bpy.data.objects.keys())
        new_objects = objects_after - objects_before

        if new_objects:
            return f"Successfully imported OBJ from '{filepath}'. Objects: {', '.join(sorted(new_objects))}"
        return f"Imported OBJ from '{filepath}' (no new objects created)"

    def import_fbx(
        self,
        filepath: str,
        use_custom_normals: bool = True,
        use_image_search: bool = True,
        ignore_leaf_bones: bool = False,
        automatic_bone_orientation: bool = False,
        global_scale: float = 1.0,
    ) -> str:
        """Imports FBX file.

        Args:
            filepath: Path to FBX file
            use_custom_normals: Use custom normals from file
            use_image_search: Search for images
            ignore_leaf_bones: Ignore leaf bones
            automatic_bone_orientation: Auto-orient bones
            global_scale: Scale factor

        Returns:
            Success message with imported object names
        """
        # Validate file exists
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"FBX file not found: {filepath}")

        # Track objects before import
        objects_before = set(bpy.data.objects.keys())

        # Import FBX
        bpy.ops.import_scene.fbx(
            filepath=filepath,
            use_custom_normals=use_custom_normals,
            use_image_search=use_image_search,
            ignore_leaf_bones=ignore_leaf_bones,
            automatic_bone_orientation=automatic_bone_orientation,
            global_scale=global_scale,
        )

        # Find newly imported objects
        objects_after = set(bpy.data.objects.keys())
        new_objects = objects_after - objects_before

        if new_objects:
            return f"Successfully imported FBX from '{filepath}'. Objects: {', '.join(sorted(new_objects))}"
        return f"Imported FBX from '{filepath}' (no new objects created)"

    def import_glb(
        self,
        filepath: str,
        import_pack_images: bool = True,
        merge_vertices: bool = False,
        import_shading: str = "NORMALS",
    ) -> str:
        """Imports GLB/GLTF file.

        Args:
            filepath: Path to GLB/GLTF file
            import_pack_images: Pack images into .blend
            merge_vertices: Merge duplicate vertices
            import_shading: Shading mode

        Returns:
            Success message with imported object names
        """
        # Validate file exists
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"GLB/GLTF file not found: {filepath}")

        # Track objects before import
        objects_before = set(bpy.data.objects.keys())

        # Import GLTF
        bpy.ops.import_scene.gltf(
            filepath=filepath,
            import_pack_images=import_pack_images,
            merge_vertices=merge_vertices,
            import_shading=import_shading,
        )

        # Find newly imported objects
        objects_after = set(bpy.data.objects.keys())
        new_objects = objects_after - objects_before

        if new_objects:
            return f"Successfully imported GLB/GLTF from '{filepath}'. Objects: {', '.join(sorted(new_objects))}"
        return f"Imported GLB/GLTF from '{filepath}' (no new objects created)"

    def import_image_as_plane(
        self,
        filepath: str,
        name: str | None = None,
        location: list[float] | None = None,
        size: float = 1.0,
        align_axis: str = "Z+",
        shader: str = "PRINCIPLED",
        use_transparency: bool = True,
    ) -> str:
        """Imports image as a textured plane.

        Args:
            filepath: Path to image file
            name: Optional name for the plane
            location: Optional [x, y, z] location
            size: Scale of the plane
            align_axis: Alignment axis
            shader: Shader type
            use_transparency: Use alpha transparency

        Returns:
            Success message with created plane name
        """
        # Validate file exists
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Image file not found: {filepath}")

        # Enable the addon if not already enabled
        addon_name = "io_import_images_as_planes"
        if addon_name not in bpy.context.preferences.addons:
            try:
                bpy.ops.preferences.addon_enable(module=addon_name)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to enable 'Import Images as Planes' addon: {e}. "
                    "This addon is required for import_image_as_plane."
                )

        # Track objects before import
        objects_before = set(bpy.data.objects.keys())

        # Map align_axis to Blender's axis format
        axis_mapping = {
            "Z+": "Z+",
            "Z-": "Z-",
            "Y+": "Y+",
            "Y-": "Y-",
            "X+": "X+",
            "X-": "X-",
        }
        blender_axis = axis_mapping.get(align_axis, "Z+")

        # Map shader type
        shader_mapping = {
            "PRINCIPLED": "PRINCIPLED",
            "SHADELESS": "SHADELESS",
            "EMISSION": "EMISSION",
        }
        blender_shader = shader_mapping.get(shader, "PRINCIPLED")

        # Get directory and filename
        directory = os.path.dirname(filepath)
        filename = os.path.basename(filepath)

        # Import image as plane
        bpy.ops.import_image.to_plane(
            files=[{"name": filename}],
            directory=directory,
            align_axis=blender_axis,
            shader=blender_shader,
            use_transparency=use_transparency,
        )

        # Find newly created object
        objects_after = set(bpy.data.objects.keys())
        new_objects = objects_after - objects_before

        if new_objects:
            # Get the newly created plane
            plane_name = list(new_objects)[0]
            plane = bpy.data.objects[plane_name]

            # Rename if custom name provided
            if name:
                plane.name = name
                plane_name = plane.name  # Get actual name (may have .001 suffix)

            # Set location if provided
            if location:
                plane.location = location

            # Scale the plane
            if size != 1.0:
                plane.scale = (size, size, size)

            return f"Successfully imported image as plane '{plane_name}' from '{filepath}'"

        return f"Imported image from '{filepath}' (plane may have merged with existing)"
