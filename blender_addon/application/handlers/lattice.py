import bpy
from typing import List, Optional, Union
from mathutils import Vector


def _vector_to_list(value):
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        return list(value)
    if hasattr(value, "to_tuple"):
        return list(value.to_tuple())
    if hasattr(value, "x"):
        coords = [value.x, value.y, value.z]
        if hasattr(value, "w"):
            coords.append(value.w)
        return coords
    try:
        return list(value)
    except TypeError:
        return [value]


class LatticeHandler:
    """Application service for lattice deformation operations."""

    def lattice_create(
        self,
        name: str = "Lattice",
        target_object: Optional[str] = None,
        location: Optional[List[float]] = None,
        points_u: int = 2,
        points_v: int = 2,
        points_w: int = 2,
        interpolation: str = "KEY_LINEAR",
    ):
        """
        [OBJECT MODE][SCENE] Creates a lattice object.

        If target_object is provided, lattice is automatically sized and positioned
        to encompass the target object's bounding box.
        """
        location = location or [0, 0, 0]

        # Validate interpolation type
        valid_interpolations = ["KEY_LINEAR", "KEY_CARDINAL", "KEY_CATMULL_ROM", "KEY_BSPLINE"]
        interpolation = interpolation.upper()
        if interpolation not in valid_interpolations:
            raise ValueError(
                f"Invalid interpolation: {interpolation}. Valid: {valid_interpolations}"
            )

        # Validate point counts (Blender allows 2-64)
        for axis_name, value in [("U", points_u), ("V", points_v), ("W", points_w)]:
            if not (2 <= value <= 64):
                raise ValueError(
                    f"points_{axis_name.lower()} must be between 2 and 64, got {value}"
                )

        # Calculate position and scale based on target object
        lattice_location = location
        lattice_scale = [1.0, 1.0, 1.0]

        if target_object:
            if target_object not in bpy.data.objects:
                raise ValueError(f"Target object '{target_object}' not found")

            target = bpy.data.objects[target_object]

            # Get world-space bounding box
            bbox_corners = [target.matrix_world @ Vector(corner) for corner in target.bound_box]

            # Calculate min/max for each axis
            min_x = min(v.x for v in bbox_corners)
            max_x = max(v.x for v in bbox_corners)
            min_y = min(v.y for v in bbox_corners)
            max_y = max(v.y for v in bbox_corners)
            min_z = min(v.z for v in bbox_corners)
            max_z = max(v.z for v in bbox_corners)

            # Add small margin (5%)
            margin = 0.05
            size_x = (max_x - min_x) * (1 + margin)
            size_y = (max_y - min_y) * (1 + margin)
            size_z = (max_z - min_z) * (1 + margin)

            # Center of bounding box
            center_x = (min_x + max_x) / 2
            center_y = (min_y + max_y) / 2
            center_z = (min_z + max_z) / 2

            lattice_location = [center_x, center_y, center_z]
            # Lattice default size is 2x2x2, so scale = desired_size / 2
            lattice_scale = [size_x / 2, size_y / 2, size_z / 2]

        # Create lattice data
        lattice_data = bpy.data.lattices.new(name)
        lattice_data.points_u = points_u
        lattice_data.points_v = points_v
        lattice_data.points_w = points_w
        lattice_data.interpolation_type_u = interpolation
        lattice_data.interpolation_type_v = interpolation
        lattice_data.interpolation_type_w = interpolation

        # Create lattice object
        lattice_obj = bpy.data.objects.new(name, lattice_data)
        lattice_obj.location = lattice_location
        lattice_obj.scale = lattice_scale

        # Link to active collection
        bpy.context.collection.objects.link(lattice_obj)

        # Ensure we're in Object Mode before selection operations
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # Select and make active
        bpy.ops.object.select_all(action='DESELECT')
        lattice_obj.select_set(True)
        bpy.context.view_layer.objects.active = lattice_obj

        total_points = points_u * points_v * points_w

        if target_object:
            return (
                f"Created lattice '{lattice_obj.name}' fitted to '{target_object}' "
                f"({points_u}x{points_v}x{points_w} = {total_points} points, "
                f"interpolation={interpolation})"
            )
        else:
            return (
                f"Created lattice '{lattice_obj.name}' at {lattice_location} "
                f"({points_u}x{points_v}x{points_w} = {total_points} points, "
                f"interpolation={interpolation})"
            )

    def lattice_bind(
        self,
        object_name: str,
        lattice_name: str,
        vertex_group: Optional[str] = None,
    ):
        """
        [OBJECT MODE][NON-DESTRUCTIVE] Binds object to lattice deformer.

        Adds a Lattice modifier to the target object pointing to the lattice.
        """
        if object_name not in bpy.data.objects:
            raise ValueError(f"Object '{object_name}' not found")

        if lattice_name not in bpy.data.objects:
            raise ValueError(f"Lattice '{lattice_name}' not found")

        obj = bpy.data.objects[object_name]
        lattice_obj = bpy.data.objects[lattice_name]

        if lattice_obj.type != 'LATTICE':
            raise ValueError(
                f"Object '{lattice_name}' is not a lattice (type: {lattice_obj.type})"
            )

        # Validate vertex group if provided
        if vertex_group:
            if obj.type != 'MESH':
                raise ValueError(
                    f"Vertex groups require mesh object, but '{object_name}' is {obj.type}"
                )
            if vertex_group not in obj.vertex_groups:
                raise ValueError(
                    f"Vertex group '{vertex_group}' not found on object '{object_name}'"
                )

        # Add Lattice modifier
        modifier = obj.modifiers.new(name=f"Lattice_{lattice_name}", type='LATTICE')
        modifier.object = lattice_obj

        if vertex_group:
            modifier.vertex_group = vertex_group

        result = (
            f"Bound '{object_name}' to lattice '{lattice_name}' "
            f"(modifier: '{modifier.name}')"
        )
        if vertex_group:
            result += f" with vertex group '{vertex_group}'"

        return result

    def lattice_edit_point(
        self,
        lattice_name: str,
        point_index: Union[int, List[int]],
        offset: List[float],
        relative: bool = True,
    ):
        """
        [OBJECT MODE] Moves lattice control points programmatically.

        Point indices go: U → V → W (fastest to slowest varying).
        """
        if lattice_name not in bpy.data.objects:
            raise ValueError(f"Lattice '{lattice_name}' not found")

        lattice_obj = bpy.data.objects[lattice_name]

        if lattice_obj.type != 'LATTICE':
            raise ValueError(
                f"Object '{lattice_name}' is not a lattice (type: {lattice_obj.type})"
            )

        lattice_data = lattice_obj.data
        total_points = len(lattice_data.points)

        # Normalize point_index to list
        if isinstance(point_index, int):
            indices = [point_index]
        else:
            indices = list(point_index)

        # Validate indices
        for idx in indices:
            if idx < 0 or idx >= total_points:
                raise ValueError(
                    f"Point index {idx} out of range (0 to {total_points - 1})"
                )

        offset_vec = Vector(offset)

        # Move points
        for idx in indices:
            point = lattice_data.points[idx]
            if relative:
                # co_deform is the deformed position (relative to rest position)
                current = Vector(point.co_deform)
                point.co_deform = current + offset_vec
            else:
                point.co_deform = offset_vec

        # Update the mesh
        lattice_data.update_tag()

        if relative:
            return (
                f"Moved {len(indices)} point(s) on '{lattice_name}' by offset {list(offset)} "
                f"(indices: {indices})"
            )
        else:
            return (
                f"Set {len(indices)} point(s) on '{lattice_name}' to position {list(offset)} "
                f"(indices: {indices})"
            )

    def get_points(self, object_name: str) -> dict:
        """
        [OBJECT MODE][READ-ONLY][SAFE] Returns lattice point positions and resolution.
        """
        if object_name not in bpy.data.objects:
            raise ValueError(f"Lattice '{object_name}' not found")

        lattice_obj = bpy.data.objects[object_name]
        if lattice_obj.type != 'LATTICE':
            raise ValueError(f"Object '{object_name}' is not a lattice (type: {lattice_obj.type})")

        lattice_data = lattice_obj.data
        points = []
        for point in lattice_data.points:
            points.append({
                "co": _vector_to_list(point.co),
                "co_deform": _vector_to_list(getattr(point, "co_deform", None))
            })

        return {
            "object_name": lattice_obj.name,
            "points_u": lattice_data.points_u,
            "points_v": lattice_data.points_v,
            "points_w": lattice_data.points_w,
            "interpolation_u": lattice_data.interpolation_type_u,
            "interpolation_v": lattice_data.interpolation_type_v,
            "interpolation_w": lattice_data.interpolation_type_w,
            "point_count": len(points),
            "points": points
        }
