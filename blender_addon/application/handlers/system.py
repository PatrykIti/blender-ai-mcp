"""System-level handler for Blender operations.

Provides low-level control over Blender state: mode switching,
undo/redo, file operations, and snapshot checkpoints.
"""
import os
import tempfile
from datetime import datetime

import bpy


class SystemHandler:
    """Application service for system-level Blender operations."""

    # Directory for storing snapshots (cleared on system temp cleanup)
    SNAPSHOT_DIR = os.path.join(tempfile.gettempdir(), "blender_ai_snapshots")

    def set_mode(self, mode, object_name=None):
        """Switch Blender context mode, optionally for a specific object.

        Args:
            mode: Target mode (OBJECT, EDIT, SCULPT, etc.)
            object_name: Optional object name to set as active before mode switch

        Returns:
            Status message describing the result
        """
        mode = mode.upper()
        valid_modes = [
            "OBJECT",
            "EDIT",
            "SCULPT",
            "VERTEX_PAINT",
            "WEIGHT_PAINT",
            "TEXTURE_PAINT",
            "POSE",
        ]

        if mode not in valid_modes:
            raise ValueError(f"Invalid mode '{mode}'. Valid: {valid_modes}")

        # If object_name provided, set it as active first
        if object_name:
            if object_name not in bpy.data.objects:
                raise ValueError(f"Object '{object_name}' not found")

            obj = bpy.data.objects[object_name]

            # Must be in OBJECT mode to change selection
            if bpy.context.mode != "OBJECT":
                bpy.ops.object.mode_set(mode="OBJECT")

            bpy.ops.object.select_all(action="DESELECT")
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

        current_mode = bpy.context.mode

        # Check if already in target mode
        if current_mode == mode or current_mode.startswith(mode):
            active_name = (
                bpy.context.active_object.name if bpy.context.active_object else "None"
            )
            return f"Already in {mode} mode (active: {active_name})"

        active_obj = bpy.context.active_object

        # Validate we have an active object for non-OBJECT modes
        if mode != "OBJECT" and not active_obj:
            raise ValueError(f"Cannot enter {mode} mode: no active object")

        # Validate object type for specific modes
        if mode == "EDIT":
            valid_types = [
                "MESH",
                "CURVE",
                "SURFACE",
                "META",
                "FONT",
                "LATTICE",
                "ARMATURE",
            ]
            if active_obj.type not in valid_types:
                raise ValueError(
                    f"Cannot enter {mode} mode: active object '{active_obj.name}' "
                    f"is type '{active_obj.type}'. Supported types: {', '.join(valid_types)}"
                )
        elif mode == "SCULPT":
            if active_obj.type != "MESH":
                raise ValueError(
                    f"Cannot enter SCULPT mode: active object '{active_obj.name}' "
                    f"is type '{active_obj.type}'. Only MESH supported."
                )
        elif mode in ["VERTEX_PAINT", "WEIGHT_PAINT", "TEXTURE_PAINT"]:
            if active_obj.type != "MESH":
                raise ValueError(
                    f"Cannot enter {mode} mode: active object '{active_obj.name}' "
                    f"is type '{active_obj.type}'. Only MESH supported."
                )
        elif mode == "POSE":
            if active_obj.type != "ARMATURE":
                raise ValueError(
                    f"Cannot enter POSE mode: active object '{active_obj.name}' "
                    f"is type '{active_obj.type}'. Only ARMATURE supported."
                )

        bpy.ops.object.mode_set(mode=mode)
        return f"Switched to {mode} mode for '{active_obj.name}'"

    def undo(self, steps=1):
        """Undo the last operation(s).

        Args:
            steps: Number of steps to undo (clamped to 1-10)

        Returns:
            Status message describing the result
        """
        # Clamp steps to safe range
        steps = max(1, min(steps, 10))

        undo_count = 0
        for _ in range(steps):
            try:
                bpy.ops.ed.undo()
                undo_count += 1
            except RuntimeError:
                # No more undo steps available
                break

        if undo_count == 0:
            return "Nothing to undo"
        elif undo_count < steps:
            return f"Undone {undo_count} step(s) (requested {steps}, reached undo limit)"
        else:
            return f"Undone {undo_count} step(s)"

    def redo(self, steps=1):
        """Redo previously undone operation(s).

        Args:
            steps: Number of steps to redo (clamped to 1-10)

        Returns:
            Status message describing the result
        """
        # Clamp steps to safe range
        steps = max(1, min(steps, 10))

        redo_count = 0
        for _ in range(steps):
            try:
                bpy.ops.ed.redo()
                redo_count += 1
            except RuntimeError:
                # No more redo steps available
                break

        if redo_count == 0:
            return "Nothing to redo"
        elif redo_count < steps:
            return f"Redone {redo_count} step(s) (requested {steps}, reached redo limit)"
        else:
            return f"Redone {redo_count} step(s)"

    def save_file(self, filepath=None, compress=True):
        """Save the current Blender file.

        Args:
            filepath: Path to save to (uses current path or temp if None)
            compress: Whether to compress the .blend file

        Returns:
            Status message with saved file path
        """
        if filepath:
            # Ensure directory exists
            dir_path = os.path.dirname(filepath)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)

            # Ensure .blend extension
            if not filepath.endswith(".blend"):
                filepath += ".blend"

            bpy.ops.wm.save_as_mainfile(filepath=filepath, compress=compress)
            return f"Saved file to '{filepath}'"
        else:
            # Try to save to current filepath
            if bpy.data.filepath:
                bpy.ops.wm.save_mainfile(compress=compress)
                return f"Saved file '{bpy.data.filepath}'"
            else:
                # Generate temp path for unsaved file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = os.path.join(
                    tempfile.gettempdir(), f"blender_ai_autosave_{timestamp}.blend"
                )
                bpy.ops.wm.save_as_mainfile(filepath=filepath, compress=compress)
                return f"Saved unsaved file to '{filepath}'"

    def new_file(self, load_ui=False):
        """Create a new Blender file (clears current scene).

        WARNING: Unsaved changes will be lost!

        Args:
            load_ui: Whether to load UI layout from startup file

        Returns:
            Status message describing the result
        """
        bpy.ops.wm.read_homefile(load_ui=load_ui)
        return "Created new file (scene reset to startup)"

    def snapshot(self, action, name=None):
        """Manage quick save/restore checkpoints.

        Args:
            action: Operation (save, restore, list, delete)
            name: Snapshot name (required for restore/delete)

        Returns:
            Status message or list of snapshots
        """
        action = action.lower()

        # Ensure snapshot directory exists
        os.makedirs(self.SNAPSHOT_DIR, exist_ok=True)

        if action == "save":
            # Generate name if not provided
            if not name:
                name = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Sanitize name (remove dangerous characters)
            safe_name = "".join(
                c for c in name if c.isalnum() or c in ("_", "-")
            ).rstrip()
            if not safe_name:
                safe_name = datetime.now().strftime("%Y%m%d_%H%M%S")

            filepath = os.path.join(self.SNAPSHOT_DIR, f"{safe_name}.blend")

            # Save as copy (doesn't change current file path)
            bpy.ops.wm.save_as_mainfile(filepath=filepath, copy=True, compress=True)
            return f"Saved snapshot '{safe_name}' to {filepath}"

        elif action == "restore":
            if not name:
                return "Error: Snapshot name required for restore"

            filepath = os.path.join(self.SNAPSHOT_DIR, f"{name}.blend")
            if not os.path.exists(filepath):
                # List available snapshots for help
                available = self._list_snapshots()
                if available:
                    return f"Snapshot '{name}' not found. Available: {', '.join(available)}"
                return f"Snapshot '{name}' not found. No snapshots available."

            bpy.ops.wm.open_mainfile(filepath=filepath)
            return f"Restored snapshot '{name}'"

        elif action == "list":
            snapshots = self._list_snapshots()
            if not snapshots:
                return "No snapshots available"

            # Get file info for each snapshot
            snapshot_info = []
            for snap_name in snapshots:
                filepath = os.path.join(self.SNAPSHOT_DIR, f"{snap_name}.blend")
                try:
                    mtime = os.path.getmtime(filepath)
                    mtime_str = datetime.fromtimestamp(mtime).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    size_mb = os.path.getsize(filepath) / (1024 * 1024)
                    snapshot_info.append(f"  - {snap_name} ({mtime_str}, {size_mb:.1f}MB)")
                except OSError:
                    snapshot_info.append(f"  - {snap_name}")

            return f"Available snapshots ({len(snapshots)}):\n" + "\n".join(snapshot_info)

        elif action == "delete":
            if not name:
                return "Error: Snapshot name required for delete"

            filepath = os.path.join(self.SNAPSHOT_DIR, f"{name}.blend")
            if not os.path.exists(filepath):
                return f"Snapshot '{name}' not found"

            os.remove(filepath)
            return f"Deleted snapshot '{name}'"

        else:
            return f"Unknown action '{action}'. Valid actions: save, restore, list, delete"

    def _list_snapshots(self):
        """List all available snapshot names.

        Returns:
            List of snapshot names (without .blend extension)
        """
        if not os.path.exists(self.SNAPSHOT_DIR):
            return []

        snapshots = []
        for filename in os.listdir(self.SNAPSHOT_DIR):
            if filename.endswith(".blend"):
                snapshots.append(filename[:-6])  # Remove .blend extension

        return sorted(snapshots)

    # === Export Tools ===

    def export_glb(
        self,
        filepath: str,
        export_selected: bool = False,
        export_animations: bool = True,
        export_materials: bool = True,
        apply_modifiers: bool = True,
    ) -> str:
        """Exports scene or selected objects to GLB/GLTF format."""
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
        """Exports scene or selected objects to FBX format."""
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
        """Exports scene or selected objects to OBJ format."""
        # Ensure correct extension
        if not filepath.lower().endswith(".obj"):
            filepath += ".obj"

        # Ensure directory exists
        dir_path = os.path.dirname(filepath)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        # Verify directory is writable
        if dir_path and not os.access(dir_path, os.W_OK):
            raise RuntimeError(f"Directory not writable: {dir_path}")

        # Check objects in scene
        mesh_objects = [obj.name for obj in bpy.data.objects if obj.type == 'MESH']
        if not mesh_objects:
            raise RuntimeError("No mesh objects in scene to export")

        # Export with OBJ exporter (Blender 4.0+ uses wm.obj_export)
        # Blender 5.0 requires check_existing=False for non-interactive export
        result = bpy.ops.wm.obj_export(
            filepath=filepath,
            check_existing=False,
            export_selected_objects=export_selected,
            apply_modifiers=apply_modifiers,
            export_materials=export_materials,
            export_uv=export_uvs,
            export_normals=export_normals,
            export_triangulated_mesh=triangulate,
        )

        # Verify export succeeded
        if result != {'FINISHED'}:
            raise RuntimeError(f"OBJ export failed with result: {result}")

        if not os.path.exists(filepath):
            raise RuntimeError(f"OBJ export failed: file was not created at {filepath}")

        return f"Successfully exported to '{filepath}'"

    # === Import Tools ===

    def import_obj(
        self,
        filepath: str,
        use_split_objects: bool = True,
        use_split_groups: bool = False,
        global_scale: float = 1.0,
        forward_axis: str = "NEGATIVE_Z",
        up_axis: str = "Y",
    ) -> str:
        """Imports OBJ file."""
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
        """Imports FBX file."""
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
        """Imports GLB/GLTF file."""
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
        name: str = None,
        location: list = None,
        size: float = 1.0,
        align_axis: str = "Z+",
        shader: str = "PRINCIPLED",
        use_transparency: bool = True,
    ) -> str:
        """Imports image as a textured plane."""
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
