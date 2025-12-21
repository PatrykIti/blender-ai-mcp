import bpy


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


class CurveHandler:
    """Application service for Curve operations."""

    # ==========================================================================
    # TASK-021: Phase 2.6 - Curves & Procedural
    # ==========================================================================

    def create_curve(self, curve_type='BEZIER', location=None):
        """
        [OBJECT MODE][SAFE] Creates a curve primitive.
        Uses bpy.ops.curve.primitive_* operators.
        """
        if location is None:
            location = (0, 0, 0)
        else:
            location = tuple(location)

        curve_type_upper = curve_type.upper()

        # Map curve types to operators
        if curve_type_upper == 'BEZIER':
            bpy.ops.curve.primitive_bezier_curve_add(location=location)
        elif curve_type_upper == 'NURBS':
            bpy.ops.curve.primitive_nurbs_curve_add(location=location)
        elif curve_type_upper == 'PATH':
            bpy.ops.curve.primitive_nurbs_path_add(location=location)
        elif curve_type_upper == 'CIRCLE':
            bpy.ops.curve.primitive_bezier_circle_add(location=location)
        else:
            raise ValueError(f"Invalid curve_type '{curve_type}'. Must be BEZIER, NURBS, PATH, or CIRCLE")

        obj = bpy.context.active_object
        return f"Created {curve_type_upper} curve '{obj.name}' at {list(location)}"

    def curve_to_mesh(self, object_name):
        """
        [OBJECT MODE][DESTRUCTIVE] Converts a curve to mesh.
        Uses bpy.ops.object.convert.
        """
        if object_name not in bpy.data.objects:
            raise ValueError(f"Object '{object_name}' not found")

        obj = bpy.data.objects[object_name]

        if obj.type not in ('CURVE', 'SURFACE', 'FONT'):
            raise ValueError(f"Object '{object_name}' is not a CURVE/SURFACE/FONT (type: {obj.type})")

        # Select the object and make it active
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        original_type = obj.type

        # Convert to mesh
        try:
            bpy.ops.object.convert(target='MESH')
        except RuntimeError as e:
            raise ValueError(f"Failed to convert '{object_name}' to mesh: {str(e)}")

        # Get the converted object (might have changed name)
        converted_obj = bpy.context.active_object

        return f"Converted {original_type} '{object_name}' to MESH '{converted_obj.name}'"

    def get_data(self, object_name):
        """
        [OBJECT MODE][READ-ONLY][SAFE] Returns curve splines, points, and settings.
        """
        if object_name not in bpy.data.objects:
            raise ValueError(f"Object '{object_name}' not found")

        obj = bpy.data.objects[object_name]
        if obj.type != 'CURVE':
            raise ValueError(f"Object '{object_name}' is not a CURVE (type: {obj.type})")

        curve_data = obj.data

        result = {
            "object_name": obj.name,
            "dimensions": curve_data.dimensions,
            "resolution_u": curve_data.resolution_u,
            "resolution_v": curve_data.resolution_v,
            "render_resolution_u": curve_data.render_resolution_u,
            "render_resolution_v": curve_data.render_resolution_v,
            "bevel_depth": curve_data.bevel_depth,
            "bevel_resolution": curve_data.bevel_resolution,
            "extrude": curve_data.extrude,
            "fill_mode": curve_data.fill_mode,
            "use_fill_caps": curve_data.use_fill_caps,
            "bevel_object": curve_data.bevel_object.name if curve_data.bevel_object else None,
            "taper_object": curve_data.taper_object.name if curve_data.taper_object else None,
            "splines": []
        }

        for spline in curve_data.splines:
            spline_entry = {
                "type": spline.type,
                "use_cyclic_u": spline.use_cyclic_u,
                "use_cyclic_v": getattr(spline, "use_cyclic_v", False),
                "order_u": getattr(spline, "order_u", None),
                "order_v": getattr(spline, "order_v", None),
                "resolution_u": spline.resolution_u,
                "resolution_v": getattr(spline, "resolution_v", None),
                "tilt_interpolation": getattr(spline, "tilt_interpolation", None),
                "radius_interpolation": getattr(spline, "radius_interpolation", None)
            }

            if spline.type == 'BEZIER':
                bezier_points = []
                for point in spline.bezier_points:
                    handle_type = point.handle_left_type
                    if point.handle_left_type != point.handle_right_type:
                        handle_type = "MIXED"
                    bezier_points.append({
                        "co": _vector_to_list(point.co),
                        "handle_left": _vector_to_list(point.handle_left),
                        "handle_right": _vector_to_list(point.handle_right),
                        "handle_left_type": point.handle_left_type,
                        "handle_right_type": point.handle_right_type,
                        "handle_type": handle_type,
                        "radius": point.radius,
                        "tilt": point.tilt,
                        "weight": getattr(point, "weight_softbody", None)
                    })
                spline_entry["bezier_points"] = bezier_points
            else:
                points = []
                for point in spline.points:
                    points.append({
                        "co": _vector_to_list(point.co),
                        "radius": point.radius,
                        "tilt": point.tilt,
                        "weight": getattr(point, "weight_softbody", None)
                    })
                spline_entry["points"] = points

            result["splines"].append(spline_entry)

        return result
