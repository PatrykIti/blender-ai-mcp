import math
import bpy

class UVHandler:
    """Application service for UV operations."""

    def list_maps(self, object_name, include_island_counts=False):
        """Lists UV maps for a specified mesh object."""
        if object_name not in bpy.data.objects:
            raise ValueError(f"Object '{object_name}' not found")

        obj = bpy.data.objects[object_name]

        # Validate that this is a mesh object
        if obj.type != 'MESH':
            raise ValueError(f"Object '{object_name}' is not a MESH (type: {obj.type})")

        # Check if object has mesh data
        if not obj.data or not hasattr(obj.data, 'uv_layers'):
            return {
                "object_name": object_name,
                "uv_map_count": 0,
                "uv_maps": []
            }

        uv_maps_data = []
        uv_layers = obj.data.uv_layers

        for uv_layer in uv_layers:
            uv_map_info = {
                "name": uv_layer.name,
                "is_active": uv_layer.active,
                "is_active_render": uv_layer.active_render,
            }

            # Optional: Include island counts (computationally expensive)
            # For now, we'll skip this and just note the number of UV loops
            if include_island_counts:
                # Number of UV coordinates (each face loop has a UV)
                uv_map_info["uv_loop_count"] = len(uv_layer.data)
                # Note: Island counting requires bmesh analysis, marked as future enhancement
                uv_map_info["island_count"] = None  # Not implemented yet

            uv_maps_data.append(uv_map_info)

        return {
            "object_name": object_name,
            "uv_map_count": len(uv_maps_data),
            "uv_maps": uv_maps_data
        }

    def unwrap(
        self,
        object_name=None,
        method="SMART_PROJECT",
        angle_limit=66.0,
        island_margin=0.02,
        scale_to_bounds=True,
    ):
        """Unwraps selected faces to UV space using specified projection method.

        Args:
            object_name: Target object (default: active object)
            method: Unwrap method ('SMART_PROJECT', 'CUBE', 'CYLINDER', 'SPHERE', 'UNWRAP')
            angle_limit: Angle threshold for SMART_PROJECT (degrees)
            island_margin: Space between UV islands
            scale_to_bounds: Scale UVs to fill 0-1 space

        Returns:
            Success message with object name and method used.
        """
        # Get target object
        if object_name:
            if object_name not in bpy.data.objects:
                raise ValueError(f"Object '{object_name}' not found")
            obj = bpy.data.objects[object_name]
        else:
            obj = bpy.context.active_object

        if obj is None:
            raise ValueError("No active object. Specify object_name or select an object.")

        if obj.type != 'MESH':
            raise ValueError(f"Object '{obj.name}' is not a mesh (type: {obj.type})")

        # Store current mode to restore later if needed
        original_mode = obj.mode

        # Ensure object is active and in Edit Mode
        bpy.context.view_layer.objects.active = obj

        if obj.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')

        # Ensure we're in face select mode for UV operations
        bpy.context.tool_settings.mesh_select_mode = (False, False, True)

        # Create UV layer if it doesn't exist
        if not obj.data.uv_layers:
            obj.data.uv_layers.new(name="UVMap")

        # Perform unwrap based on method
        if method == "SMART_PROJECT":
            bpy.ops.uv.smart_project(
                angle_limit=math.radians(angle_limit),
                island_margin=island_margin,
                scale_to_bounds=scale_to_bounds
            )
        elif method == "CUBE":
            bpy.ops.uv.cube_project(
                scale_to_bounds=scale_to_bounds
            )
        elif method == "CYLINDER":
            bpy.ops.uv.cylinder_project(
                scale_to_bounds=scale_to_bounds
            )
        elif method == "SPHERE":
            bpy.ops.uv.sphere_project(
                scale_to_bounds=scale_to_bounds
            )
        elif method == "UNWRAP":
            bpy.ops.uv.unwrap(
                method='ANGLE_BASED',
                margin=island_margin
            )
        else:
            raise ValueError(f"Unknown unwrap method: {method}")

        return f"Unwrapped '{obj.name}' using {method}"

    def pack_islands(
        self,
        object_name=None,
        margin=0.02,
        rotate=True,
        scale=True,
    ):
        """Packs UV islands for optimal texture space usage.

        Args:
            object_name: Target object (default: active object)
            margin: Space between packed islands
            rotate: Allow rotation for better packing
            scale: Allow scaling islands to fill space

        Returns:
            Success message with object name.
        """
        # Get target object
        if object_name:
            if object_name not in bpy.data.objects:
                raise ValueError(f"Object '{object_name}' not found")
            obj = bpy.data.objects[object_name]
        else:
            obj = bpy.context.active_object

        if obj is None:
            raise ValueError("No active object. Specify object_name or select an object.")

        if obj.type != 'MESH':
            raise ValueError(f"Object '{obj.name}' is not a mesh (type: {obj.type})")

        # Ensure object is active and in Edit Mode
        bpy.context.view_layer.objects.active = obj

        if obj.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')

        # Select all UVs in UV editor
        bpy.ops.uv.select_all(action='SELECT')

        # Pack islands
        bpy.ops.uv.pack_islands(
            margin=margin,
            rotate=rotate,
            scale=scale
        )

        return f"Packed UV islands for '{obj.name}'"

    def create_seam(
        self,
        object_name=None,
        action="mark",
    ):
        """Marks or clears UV seams on selected edges.

        Args:
            object_name: Target object (default: active object)
            action: 'mark' to add seams, 'clear' to remove seams

        Returns:
            Success message describing the action taken.
        """
        # Get target object
        if object_name:
            if object_name not in bpy.data.objects:
                raise ValueError(f"Object '{object_name}' not found")
            obj = bpy.data.objects[object_name]
        else:
            obj = bpy.context.active_object

        if obj is None:
            raise ValueError("No active object. Specify object_name or select an object.")

        if obj.type != 'MESH':
            raise ValueError(f"Object '{obj.name}' is not a mesh (type: {obj.type})")

        # Ensure object is active and in Edit Mode
        bpy.context.view_layer.objects.active = obj

        if obj.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')

        # Ensure edge select mode
        bpy.context.tool_settings.mesh_select_mode = (False, True, False)

        # Mark or clear seams
        if action == "mark":
            bpy.ops.mesh.mark_seam(clear=False)
            return f"Marked seams on selected edges of '{obj.name}'"
        elif action == "clear":
            bpy.ops.mesh.mark_seam(clear=True)
            return f"Cleared seams from selected edges of '{obj.name}'"
        else:
            raise ValueError(f"Unknown action: {action}. Use 'mark' or 'clear'.")
