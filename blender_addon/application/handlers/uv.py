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
