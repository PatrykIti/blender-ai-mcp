import bpy
from typing import List, Optional


class SculptHandler:
    """Application service for Sculpt Mode operations in Blender."""

    def _ensure_sculpt_mode(self, object_name: Optional[str] = None):
        """
        Ensures the target object is a Mesh and in Sculpt Mode.

        Args:
            object_name: Name of the object to target, or None for active object.

        Returns:
            tuple: (obj, previous_mode)

        Raises:
            ValueError: If object is not found or not a mesh.
        """
        if object_name:
            obj = bpy.data.objects.get(object_name)
            if not obj:
                raise ValueError(f"Object '{object_name}' not found")
            # Set as active
            bpy.context.view_layer.objects.active = obj
        else:
            obj = bpy.context.active_object

        if not obj or obj.type != 'MESH':
            raise ValueError(
                f"Object '{object_name or 'active'}' is not a mesh. "
                f"Type: {obj.type if obj else 'None'}"
            )

        previous_mode = obj.mode

        if previous_mode != 'SCULPT':
            bpy.ops.object.mode_set(mode='SCULPT')

        return obj, previous_mode

    def _set_symmetry(self, obj, use_symmetry: bool, axis: str):
        """
        Configures sculpt symmetry settings.

        Args:
            obj: The mesh object.
            use_symmetry: Whether to enable symmetry.
            axis: The axis for symmetry (X, Y, or Z).
        """
        axis = axis.upper()
        # In Blender 5.0+, symmetry is on sculpt tool settings
        sculpt = bpy.context.scene.tool_settings.sculpt

        # Reset all axes first
        sculpt.use_symmetry_x = False
        sculpt.use_symmetry_y = False
        sculpt.use_symmetry_z = False

        if use_symmetry:
            if axis == 'X':
                sculpt.use_symmetry_x = True
            elif axis == 'Y':
                sculpt.use_symmetry_y = True
            elif axis == 'Z':
                sculpt.use_symmetry_z = True

    # ==========================================================================
    # TASK-027-1: sculpt_auto (Mesh Filters)
    # ==========================================================================

    def auto_sculpt(
        self,
        object_name: Optional[str] = None,
        operation: str = "smooth",
        strength: float = 0.5,
        iterations: int = 1,
        use_symmetry: bool = True,
        symmetry_axis: str = "X",
    ) -> str:
        """
        High-level sculpt operation applied to entire mesh using mesh filters.

        Args:
            object_name: Target object (default: active object)
            operation: 'smooth', 'inflate', 'flatten', 'sharpen'
            strength: Operation strength 0-1
            iterations: Number of passes
            use_symmetry: Enable symmetry
            symmetry_axis: Symmetry axis (X, Y, Z)

        Returns:
            Success message describing the operation performed.
        """
        obj, previous_mode = self._ensure_sculpt_mode(object_name)

        # Set symmetry
        self._set_symmetry(obj, use_symmetry, symmetry_axis)

        # Clamp values
        strength = max(0.0, min(1.0, strength))
        iterations = max(1, iterations)

        # Map operation to mesh filter type
        # Blender 5.0 available: SMOOTH, SCALE, INFLATE, SPHERE, RANDOM, RELAX,
        # RELAX_FACE_SETS, SURFACE_SMOOTH, SHARPEN, ENHANCE_DETAILS, ERASE_DISPLACEMENT
        operation = operation.upper()
        filter_map = {
            'SMOOTH': 'SMOOTH',
            'INFLATE': 'INFLATE',
            'FLATTEN': 'SURFACE_SMOOTH',  # FLATTEN removed in Blender 5.0
            'SHARPEN': 'SHARPEN',
        }

        if operation not in filter_map:
            valid_ops = ', '.join(filter_map.keys())
            raise ValueError(
                f"Invalid operation '{operation}'. Valid: {valid_ops}"
            )

        filter_type = filter_map[operation]

        # Apply mesh filter for each iteration
        for _ in range(iterations):
            bpy.ops.sculpt.mesh_filter(type=filter_type, strength=strength)

        symmetry_str = f" (symmetry: {symmetry_axis})" if use_symmetry else ""
        return (
            f"Applied {operation.lower()} to '{obj.name}' "
            f"({iterations} iterations, strength={strength}){symmetry_str}"
        )

    # ==========================================================================
    # TASK-027-2: sculpt_brush_smooth
    # ==========================================================================

    def brush_smooth(
        self,
        object_name: Optional[str] = None,
        location: Optional[List[float]] = None,
        radius: float = 0.1,
        strength: float = 0.5,
    ) -> str:
        """
        Applies smooth brush at specified location.

        Note: Programmatic brush strokes are complex in Blender.
        This sets up the brush. For whole-mesh smoothing, use auto_sculpt.

        Args:
            object_name: Target object (default: active object)
            location: World position [x, y, z] for brush center
            radius: Brush radius in Blender units
            strength: Brush strength 0-1

        Returns:
            Success message.
        """
        obj, previous_mode = self._ensure_sculpt_mode(object_name)

        # Clamp values
        radius = max(0.001, radius)
        strength = max(0.0, min(1.0, strength))

        # Get or create smooth brush
        tool_settings = bpy.context.tool_settings
        sculpt = tool_settings.sculpt

        # Select smooth brush using the tool system
        bpy.ops.wm.tool_set_by_id(name="builtin_brush.Smooth")

        # Configure brush settings
        brush = sculpt.brush
        if brush:
            # Convert radius to screen pixels (approximate conversion)
            # Blender uses unified_size for radius in pixels
            brush.size = int(radius * 200)  # Approximate conversion
            brush.strength = strength

        location_str = f" at {location}" if location else ""
        return (
            f"Smooth brush ready on '{obj.name}' "
            f"(radius={radius}, strength={strength}){location_str}. "
            f"Note: Use sculpt_auto for whole-mesh smoothing."
        )

    # ==========================================================================
    # TASK-027-3: sculpt_brush_grab
    # ==========================================================================

    def brush_grab(
        self,
        object_name: Optional[str] = None,
        from_location: Optional[List[float]] = None,
        to_location: Optional[List[float]] = None,
        radius: float = 0.1,
        strength: float = 0.5,
    ) -> str:
        """
        Grabs and moves geometry from one location to another.

        Note: Programmatic brush strokes are complex in Blender.
        This sets up the brush.

        Args:
            object_name: Target object (default: active object)
            from_location: Start position [x, y, z]
            to_location: End position [x, y, z]
            radius: Brush radius
            strength: Brush strength 0-1

        Returns:
            Success message.
        """
        obj, previous_mode = self._ensure_sculpt_mode(object_name)

        # Clamp values
        radius = max(0.001, radius)
        strength = max(0.0, min(1.0, strength))

        # Get tool settings
        tool_settings = bpy.context.tool_settings
        sculpt = tool_settings.sculpt

        # Select grab brush
        bpy.ops.wm.tool_set_by_id(name="builtin_brush.Grab")

        # Configure brush settings
        brush = sculpt.brush
        if brush:
            brush.size = int(radius * 200)
            brush.strength = strength

        from_str = f" from {from_location}" if from_location else ""
        to_str = f" to {to_location}" if to_location else ""
        return (
            f"Grab brush ready on '{obj.name}' "
            f"(radius={radius}, strength={strength}){from_str}{to_str}. "
            f"Note: Programmatic grab strokes require manual interaction."
        )

    # ==========================================================================
    # TASK-027-4: sculpt_brush_crease
    # ==========================================================================

    def brush_crease(
        self,
        object_name: Optional[str] = None,
        location: Optional[List[float]] = None,
        radius: float = 0.1,
        strength: float = 0.5,
        pinch: float = 0.5,
    ) -> str:
        """
        Creates sharp crease at specified location.

        Note: Programmatic brush strokes are complex in Blender.
        This sets up the brush.

        Args:
            object_name: Target object (default: active object)
            location: World position [x, y, z]
            radius: Brush radius
            strength: Brush strength 0-1
            pinch: Pinch amount for sharper creases

        Returns:
            Success message.
        """
        obj, previous_mode = self._ensure_sculpt_mode(object_name)

        # Clamp values
        radius = max(0.001, radius)
        strength = max(0.0, min(1.0, strength))
        pinch = max(0.0, min(1.0, pinch))

        # Get tool settings
        tool_settings = bpy.context.tool_settings
        sculpt = tool_settings.sculpt

        # Select crease brush
        bpy.ops.wm.tool_set_by_id(name="builtin_brush.Crease")

        # Configure brush settings
        brush = sculpt.brush
        if brush:
            brush.size = int(radius * 200)
            brush.strength = strength
            # Crease brush has a pinch factor in its settings
            if hasattr(brush, 'crease_pinch_factor'):
                brush.crease_pinch_factor = pinch

        location_str = f" at {location}" if location else ""
        return (
            f"Crease brush ready on '{obj.name}' "
            f"(radius={radius}, strength={strength}, pinch={pinch}){location_str}. "
            f"Note: For sharp edges, consider mesh_bevel with edge selection."
        )
