import bpy


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
