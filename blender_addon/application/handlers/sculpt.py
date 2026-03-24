import math
from typing import List, Optional

import bpy


class SculptHandler:
    """Application service for Sculpt Mode operations in Blender."""

    @staticmethod
    def _coerce_xyz(value) -> tuple[float, float, float]:
        """Convert any vector-like value to a plain xyz tuple."""

        return (float(value[0]), float(value[1]), float(value[2]))

    @staticmethod
    def _set_xyz(target, value: tuple[float, float, float]) -> None:
        """Assign xyz coordinates onto a Vector-like target."""

        try:
            target.x = value[0]
            target.y = value[1]
            target.z = value[2]
            return
        except Exception:
            pass

        target[0] = value[0]
        target[1] = value[1]
        target[2] = value[2]

    @staticmethod
    def _distance(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
        """Return Euclidean distance between two xyz tuples."""

        return math.sqrt(sum((left - right) ** 2 for left, right in zip(a, b)))

    @staticmethod
    def _falloff_weight(distance: float, radius: float, falloff: str) -> float:
        """Return normalized falloff weight for one distance/radius pair."""

        if radius <= 0:
            raise ValueError("Radius must be > 0")

        if distance >= radius:
            return 0.0

        t = max(0.0, min(distance / radius, 1.0))
        mode = falloff.upper()

        if mode == "CONSTANT":
            return 1.0
        if mode == "LINEAR":
            return 1.0 - t
        if mode == "SHARP":
            return (1.0 - t) ** 2
        if mode == "SMOOTH":
            return 1.0 - (3.0 * t * t - 2.0 * t * t * t)

        raise ValueError(f"Invalid falloff '{falloff}'. Expected SMOOTH, LINEAR, SHARP, or CONSTANT.")

    @staticmethod
    def _mirror_axis_index(axis: str) -> int:
        """Resolve symmetry axis to xyz index."""

        normalized = axis.upper()
        mapping = {"X": 0, "Y": 1, "Z": 2}
        if normalized not in mapping:
            raise ValueError(f"Invalid symmetry axis '{axis}'. Expected X, Y, or Z.")
        return mapping[normalized]

    def _ensure_mesh_object_mode(self, object_name: Optional[str] = None):
        """Ensure the target object exists, is a mesh, and is editable in Object Mode."""

        if object_name:
            obj = bpy.data.objects.get(object_name)
            if not obj:
                raise ValueError(f"Object '{object_name}' not found")
            bpy.context.view_layer.objects.active = obj
        else:
            obj = bpy.context.active_object

        if not obj or obj.type != "MESH":
            raise ValueError(f"Object '{object_name or 'active'}' is not a mesh. Type: {obj.type if obj else 'None'}")

        previous_mode = obj.mode
        if previous_mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        return obj, previous_mode

    def _restore_mode(self, previous_mode: str) -> None:
        """Best-effort restoration of the previous Blender interaction mode."""

        if previous_mode and previous_mode != "OBJECT":
            try:
                bpy.ops.object.mode_set(mode=previous_mode)
            except Exception:
                pass

    def _world_point_to_local(self, obj, point: tuple[float, float, float]) -> tuple[float, float, float]:
        """Convert world-space point to local coordinates when matrix data is available."""

        matrix_world = getattr(obj, "matrix_world", None)
        if matrix_world is None:
            return point

        try:
            from mathutils import Vector

            local = matrix_world.inverted() @ Vector(point)
            return self._coerce_xyz(local)
        except Exception:
            return point

    def _world_vector_to_local(self, obj, vector: tuple[float, float, float]) -> tuple[float, float, float]:
        """Convert world-space displacement vector to local coordinates when possible."""

        matrix_world = getattr(obj, "matrix_world", None)
        if matrix_world is None:
            return vector

        try:
            from mathutils import Vector

            inverse = matrix_world.inverted()
            local = inverse.to_3x3() @ Vector(vector)
            return self._coerce_xyz(local)
        except Exception:
            return vector

    @staticmethod
    def _vector_length(vector: tuple[float, float, float]) -> float:
        """Return vector length."""

        return math.sqrt(sum(component * component for component in vector))

    def _normalize_vector(self, vector: tuple[float, float, float]) -> tuple[float, float, float]:
        """Return normalized vector or zero vector when length is zero."""

        length = self._vector_length(vector)
        if length == 0:
            return (0.0, 0.0, 0.0)
        return tuple(component / length for component in vector)

    def _strongest_region_source(
        self,
        vertex_co: tuple[float, float, float],
        center: tuple[float, float, float],
        radius: float,
        falloff: str,
        use_symmetry: bool,
        symmetry_axis: str,
    ) -> tuple[float, tuple[float, float, float], bool]:
        """Return the strongest local region source for one vertex."""

        primary_weight = self._falloff_weight(self._distance(vertex_co, center), radius, falloff)
        best_weight = primary_weight
        best_center = center
        mirrored = False

        if use_symmetry:
            axis_index = self._mirror_axis_index(symmetry_axis)
            mirrored_center = list(center)
            mirrored_center[axis_index] *= -1.0

            mirror_weight = self._falloff_weight(
                self._distance(vertex_co, tuple(mirrored_center)),
                radius,
                falloff,
            )
            if mirror_weight > best_weight:
                best_weight = mirror_weight
                best_center = tuple(mirrored_center)
                mirrored = True

        return best_weight, best_center, mirrored

    @staticmethod
    def _build_vertex_adjacency(obj) -> dict[int, set[int]]:
        """Build one-hop adjacency map from mesh edges."""

        vertices = list(getattr(obj.data, "vertices", []))
        adjacency = {index: set() for index in range(len(vertices))}

        for edge in getattr(obj.data, "edges", []):
            vert_indices = getattr(edge, "vertices", None)
            if vert_indices is None or len(vert_indices) != 2:
                continue
            left, right = int(vert_indices[0]), int(vert_indices[1])
            adjacency.setdefault(left, set()).add(right)
            adjacency.setdefault(right, set()).add(left)

        return adjacency

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

        if not obj or obj.type != "MESH":
            raise ValueError(f"Object '{object_name or 'active'}' is not a mesh. Type: {obj.type if obj else 'None'}")

        previous_mode = obj.mode

        if previous_mode != "SCULPT":
            bpy.ops.object.mode_set(mode="SCULPT")

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
            if axis == "X":
                sculpt.use_symmetry_x = True
            elif axis == "Y":
                sculpt.use_symmetry_y = True
            elif axis == "Z":
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
            "SMOOTH": "SMOOTH",
            "INFLATE": "INFLATE",
            "FLATTEN": "SURFACE_SMOOTH",  # FLATTEN removed in Blender 5.0
            "SHARPEN": "SHARPEN",
        }

        if operation not in filter_map:
            valid_ops = ", ".join(filter_map.keys())
            raise ValueError(f"Invalid operation '{operation}'. Valid: {valid_ops}")

        filter_type = filter_map[operation]

        # Apply mesh filter for each iteration
        for _ in range(iterations):
            bpy.ops.sculpt.mesh_filter(type=filter_type, strength=strength)

        symmetry_str = f" (symmetry: {symmetry_axis})" if use_symmetry else ""
        return (
            f"Applied {operation.lower()} to '{obj.name}' ({iterations} iterations, strength={strength}){symmetry_str}"
        )

    def deform_region(
        self,
        object_name: Optional[str] = None,
        center: Optional[List[float]] = None,
        radius: float = 0.5,
        delta: Optional[List[float]] = None,
        strength: float = 1.0,
        falloff: str = "SMOOTH",
        use_symmetry: bool = False,
        symmetry_axis: str = "X",
    ) -> dict:
        """
        Deterministically deforms a local region of mesh vertices.

        This is a geometry-driven replacement for UI brush grab behavior.
        """
        if center is None:
            raise ValueError("center is required")
        if delta is None:
            raise ValueError("delta is required")
        if radius <= 0:
            raise ValueError("radius must be > 0")

        clamped_strength = max(0.0, min(1.0, strength))
        center_xyz = self._coerce_xyz(center)
        delta_xyz = self._coerce_xyz(delta)

        obj, previous_mode = self._ensure_mesh_object_mode(object_name)

        try:
            center_local = self._world_point_to_local(obj, center_xyz)
            delta_local = self._world_vector_to_local(obj, delta_xyz)

            affected_vertices = 0
            max_weight = 0.0

            for vertex in getattr(obj.data, "vertices", []):
                vertex_co = self._coerce_xyz(vertex.co)
                base_weight, _chosen_center, mirrored = self._strongest_region_source(
                    vertex_co=vertex_co,
                    center=center_local,
                    radius=radius,
                    falloff=falloff,
                    use_symmetry=use_symmetry,
                    symmetry_axis=symmetry_axis,
                )
                chosen_delta = delta_local
                if mirrored:
                    axis_index = self._mirror_axis_index(symmetry_axis)
                    mirrored_delta = list(delta_local)
                    mirrored_delta[axis_index] *= -1.0
                    chosen_delta = tuple(mirrored_delta)

                weight = base_weight * clamped_strength

                if weight <= 0:
                    continue

                new_co = tuple(vertex_co[i] + chosen_delta[i] * weight for i in range(3))
                self._set_xyz(vertex.co, new_co)
                affected_vertices += 1
                max_weight = max(max_weight, weight)

            if hasattr(obj.data, "update"):
                obj.data.update()

            return {
                "object_name": obj.name,
                "affected_vertices": affected_vertices,
                "radius": radius,
                "strength": clamped_strength,
                "falloff": falloff.upper(),
                "use_symmetry": use_symmetry,
                "symmetry_axis": symmetry_axis.upper() if use_symmetry else None,
                "center": list(center_xyz),
                "delta": list(delta_xyz),
                "max_weight": round(max_weight, 6),
            }
        finally:
            self._restore_mode(previous_mode)

    def smooth_region(
        self,
        object_name: Optional[str] = None,
        center: Optional[List[float]] = None,
        radius: float = 0.5,
        strength: float = 0.5,
        iterations: int = 1,
        falloff: str = "SMOOTH",
        use_symmetry: bool = False,
        symmetry_axis: str = "X",
    ) -> dict:
        """Deterministically smooth a local mesh region using edge-adjacency averaging."""

        if center is None:
            raise ValueError("center is required")
        if radius <= 0:
            raise ValueError("radius must be > 0")

        clamped_strength = max(0.0, min(1.0, strength))
        iterations = max(1, int(iterations))
        center_xyz = self._coerce_xyz(center)

        obj, previous_mode = self._ensure_mesh_object_mode(object_name)

        try:
            center_local = self._world_point_to_local(obj, center_xyz)
            vertices = list(getattr(obj.data, "vertices", []))
            adjacency = self._build_vertex_adjacency(obj)

            weights: dict[int, float] = {}
            for index, vertex in enumerate(vertices):
                vertex_co = self._coerce_xyz(vertex.co)
                base_weight, _chosen_center, _mirrored = self._strongest_region_source(
                    vertex_co=vertex_co,
                    center=center_local,
                    radius=radius,
                    falloff=falloff,
                    use_symmetry=use_symmetry,
                    symmetry_axis=symmetry_axis,
                )
                if base_weight > 0 and adjacency.get(index):
                    weights[index] = base_weight * clamped_strength

            for _ in range(iterations):
                snapshot = [self._coerce_xyz(vertex.co) for vertex in vertices]
                next_positions: dict[int, tuple[float, float, float]] = {}

                for index, weight in weights.items():
                    neighbors = adjacency.get(index, set())
                    if not neighbors:
                        continue
                    neighbor_average = tuple(
                        sum(snapshot[neighbor][axis] for neighbor in neighbors) / len(neighbors) for axis in range(3)
                    )
                    current = snapshot[index]
                    next_positions[index] = tuple(
                        current[axis] + (neighbor_average[axis] - current[axis]) * weight for axis in range(3)
                    )

                for index, new_co in next_positions.items():
                    self._set_xyz(vertices[index].co, new_co)

            if hasattr(obj.data, "update"):
                obj.data.update()

            return {
                "object_name": obj.name,
                "affected_vertices": len(weights),
                "radius": radius,
                "strength": clamped_strength,
                "iterations": iterations,
                "falloff": falloff.upper(),
                "use_symmetry": use_symmetry,
                "symmetry_axis": symmetry_axis.upper() if use_symmetry else None,
                "center": list(center_xyz),
            }
        finally:
            self._restore_mode(previous_mode)

    def inflate_region(
        self,
        object_name: Optional[str] = None,
        center: Optional[List[float]] = None,
        radius: float = 0.5,
        amount: float = 0.2,
        falloff: str = "SMOOTH",
        use_symmetry: bool = False,
        symmetry_axis: str = "X",
    ) -> dict:
        """Deterministically inflate or deflate a local region."""

        if center is None:
            raise ValueError("center is required")
        if radius <= 0:
            raise ValueError("radius must be > 0")

        center_xyz = self._coerce_xyz(center)

        obj, previous_mode = self._ensure_mesh_object_mode(object_name)

        try:
            center_local = self._world_point_to_local(obj, center_xyz)
            affected_vertices = 0

            for vertex in getattr(obj.data, "vertices", []):
                vertex_co = self._coerce_xyz(vertex.co)
                base_weight, chosen_center, _mirrored = self._strongest_region_source(
                    vertex_co=vertex_co,
                    center=center_local,
                    radius=radius,
                    falloff=falloff,
                    use_symmetry=use_symmetry,
                    symmetry_axis=symmetry_axis,
                )
                if base_weight <= 0:
                    continue

                normal_source = getattr(vertex, "normal", None)
                if normal_source is not None:
                    direction = self._normalize_vector(self._coerce_xyz(normal_source))
                else:
                    direction = self._normalize_vector(tuple(vertex_co[axis] - chosen_center[axis] for axis in range(3)))

                new_co = tuple(vertex_co[axis] + direction[axis] * amount * base_weight for axis in range(3))
                self._set_xyz(vertex.co, new_co)
                affected_vertices += 1

            if hasattr(obj.data, "update"):
                obj.data.update()

            return {
                "object_name": obj.name,
                "affected_vertices": affected_vertices,
                "radius": radius,
                "amount": amount,
                "falloff": falloff.upper(),
                "use_symmetry": use_symmetry,
                "symmetry_axis": symmetry_axis.upper() if use_symmetry else None,
                "center": list(center_xyz),
            }
        finally:
            self._restore_mode(previous_mode)

    def pinch_region(
        self,
        object_name: Optional[str] = None,
        center: Optional[List[float]] = None,
        radius: float = 0.5,
        amount: float = 0.2,
        falloff: str = "SMOOTH",
        use_symmetry: bool = False,
        symmetry_axis: str = "X",
    ) -> dict:
        """Deterministically pinch a local region toward the influence center."""

        if center is None:
            raise ValueError("center is required")
        if radius <= 0:
            raise ValueError("radius must be > 0")

        center_xyz = self._coerce_xyz(center)

        obj, previous_mode = self._ensure_mesh_object_mode(object_name)

        try:
            center_local = self._world_point_to_local(obj, center_xyz)
            affected_vertices = 0

            for vertex in getattr(obj.data, "vertices", []):
                vertex_co = self._coerce_xyz(vertex.co)
                base_weight, chosen_center, _mirrored = self._strongest_region_source(
                    vertex_co=vertex_co,
                    center=center_local,
                    radius=radius,
                    falloff=falloff,
                    use_symmetry=use_symmetry,
                    symmetry_axis=symmetry_axis,
                )
                if base_weight <= 0:
                    continue

                direction = self._normalize_vector(tuple(chosen_center[axis] - vertex_co[axis] for axis in range(3)))
                new_co = tuple(vertex_co[axis] + direction[axis] * amount * base_weight for axis in range(3))
                self._set_xyz(vertex.co, new_co)
                affected_vertices += 1

            if hasattr(obj.data, "update"):
                obj.data.update()

            return {
                "object_name": obj.name,
                "affected_vertices": affected_vertices,
                "radius": radius,
                "amount": amount,
                "falloff": falloff.upper(),
                "use_symmetry": use_symmetry,
                "symmetry_axis": symmetry_axis.upper() if use_symmetry else None,
                "center": list(center_xyz),
            }
        finally:
            self._restore_mode(previous_mode)

    def crease_region(
        self,
        object_name: Optional[str] = None,
        center: Optional[List[float]] = None,
        radius: float = 0.5,
        depth: float = 0.1,
        pinch: float = 0.5,
        falloff: str = "SMOOTH",
        use_symmetry: bool = False,
        symmetry_axis: str = "X",
    ) -> dict:
        """Deterministically create a local crease/groove region."""

        if center is None:
            raise ValueError("center is required")
        if radius <= 0:
            raise ValueError("radius must be > 0")

        clamped_pinch = max(0.0, min(1.0, pinch))
        center_xyz = self._coerce_xyz(center)

        obj, previous_mode = self._ensure_mesh_object_mode(object_name)

        try:
            center_local = self._world_point_to_local(obj, center_xyz)
            affected_vertices = 0

            for vertex in getattr(obj.data, "vertices", []):
                vertex_co = self._coerce_xyz(vertex.co)
                base_weight, chosen_center, _mirrored = self._strongest_region_source(
                    vertex_co=vertex_co,
                    center=center_local,
                    radius=radius,
                    falloff=falloff,
                    use_symmetry=use_symmetry,
                    symmetry_axis=symmetry_axis,
                )
                if base_weight <= 0:
                    continue

                normal_source = getattr(vertex, "normal", None)
                if normal_source is not None:
                    inward_normal = tuple(
                        -component for component in self._normalize_vector(self._coerce_xyz(normal_source))
                    )
                else:
                    inward_normal = self._normalize_vector(
                        tuple(chosen_center[axis] - vertex_co[axis] for axis in range(3))
                    )

                to_center = self._normalize_vector(tuple(chosen_center[axis] - vertex_co[axis] for axis in range(3)))
                new_co = tuple(
                    vertex_co[axis]
                    + (inward_normal[axis] * depth + to_center[axis] * depth * clamped_pinch) * base_weight
                    for axis in range(3)
                )
                self._set_xyz(vertex.co, new_co)
                affected_vertices += 1

            if hasattr(obj.data, "update"):
                obj.data.update()

            return {
                "object_name": obj.name,
                "affected_vertices": affected_vertices,
                "radius": radius,
                "depth": depth,
                "pinch": clamped_pinch,
                "falloff": falloff.upper(),
                "use_symmetry": use_symmetry,
                "symmetry_axis": symmetry_axis.upper() if use_symmetry else None,
                "center": list(center_xyz),
            }
        finally:
            self._restore_mode(previous_mode)

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
        Configures the Grab brush for manual interaction.

        Note: Programmatic grab strokes are not executed here.
        This only sets up the brush and context for a human-driven stroke.

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
            f"Grab brush configured on '{obj.name}' "
            f"(radius={radius}, strength={strength}){from_str}{to_str}. "
            f"No geometry was modified. Manual interaction is required to perform the grab stroke."
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
            if hasattr(brush, "crease_pinch_factor"):
                brush.crease_pinch_factor = pinch

        location_str = f" at {location}" if location else ""
        return (
            f"Crease brush ready on '{obj.name}' "
            f"(radius={radius}, strength={strength}, pinch={pinch}){location_str}. "
            f"Note: For sharp edges, consider mesh_bevel with edge selection."
        )

    # ==========================================================================
    # TASK-038-2: Core Sculpt Brushes
    # ==========================================================================

    def brush_clay(
        self,
        object_name: Optional[str] = None,
        radius: float = 0.1,
        strength: float = 0.5,
    ) -> str:
        """
        Sets up Clay brush for adding material.

        Adds material like clay - builds up surface.
        Essential for: muscle mass, fat deposits, organ volume.
        """
        obj, previous_mode = self._ensure_sculpt_mode(object_name)

        # Clamp values
        radius = max(0.001, radius)
        strength = max(0.0, min(1.0, strength))

        # Get tool settings
        tool_settings = bpy.context.tool_settings
        sculpt = tool_settings.sculpt

        # Select clay brush
        bpy.ops.wm.tool_set_by_id(name="builtin_brush.Clay")

        # Configure brush settings
        brush = sculpt.brush
        if brush:
            brush.size = int(radius * 200)
            brush.strength = strength

        return (
            f"Clay brush ready on '{obj.name}' "
            f"(radius={radius}, strength={strength}). "
            f"Builds up surface like sculpting clay."
        )

    def brush_inflate(
        self,
        object_name: Optional[str] = None,
        radius: float = 0.1,
        strength: float = 0.5,
    ) -> str:
        """
        Sets up Inflate brush for pushing geometry outward.

        Pushes geometry outward along normals - inflates like balloon.
        Essential for: swelling, tumors, blisters, organ volume.
        """
        obj, previous_mode = self._ensure_sculpt_mode(object_name)

        # Clamp values
        radius = max(0.001, radius)
        strength = max(0.0, min(1.0, strength))

        # Get tool settings
        tool_settings = bpy.context.tool_settings
        sculpt = tool_settings.sculpt

        # Select inflate brush
        bpy.ops.wm.tool_set_by_id(name="builtin_brush.Inflate")

        # Configure brush settings
        brush = sculpt.brush
        if brush:
            brush.size = int(radius * 200)
            brush.strength = strength

        return (
            f"Inflate brush ready on '{obj.name}' "
            f"(radius={radius}, strength={strength}). "
            f"Pushes geometry outward along normals."
        )

    def brush_blob(
        self,
        object_name: Optional[str] = None,
        radius: float = 0.1,
        strength: float = 0.5,
    ) -> str:
        """
        Sets up Blob brush for creating rounded organic bulges.

        Creates rounded, organic bulges.
        Essential for: nodules, bumps, organic growths.
        """
        obj, previous_mode = self._ensure_sculpt_mode(object_name)

        # Clamp values
        radius = max(0.001, radius)
        strength = max(0.0, min(1.0, strength))

        # Get tool settings
        tool_settings = bpy.context.tool_settings
        sculpt = tool_settings.sculpt

        # Select blob brush
        bpy.ops.wm.tool_set_by_id(name="builtin_brush.Blob")

        # Configure brush settings
        brush = sculpt.brush
        if brush:
            brush.size = int(radius * 200)
            brush.strength = strength

        return (
            f"Blob brush ready on '{obj.name}' (radius={radius}, strength={strength}). Creates rounded organic bulges."
        )

    # ==========================================================================
    # TASK-038-3: Detail Sculpt Brushes
    # ==========================================================================

    def brush_snake_hook(
        self,
        object_name: Optional[str] = None,
        radius: float = 0.1,
        strength: float = 0.5,
    ) -> str:
        """
        Sets up Snake Hook brush for pulling geometry like taffy.

        Pulls geometry like taffy - creates long tendrils.
        Essential for: blood vessels, nerves, tentacles, organic protrusions.
        """
        obj, previous_mode = self._ensure_sculpt_mode(object_name)

        # Clamp values
        radius = max(0.001, radius)
        strength = max(0.0, min(1.0, strength))

        # Get tool settings
        tool_settings = bpy.context.tool_settings
        sculpt = tool_settings.sculpt

        # Select snake hook brush
        bpy.ops.wm.tool_set_by_id(name="builtin_brush.Snake Hook")

        # Configure brush settings
        brush = sculpt.brush
        if brush:
            brush.size = int(radius * 200)
            brush.strength = strength

        return (
            f"Snake Hook brush ready on '{obj.name}' "
            f"(radius={radius}, strength={strength}). "
            f"Pulls geometry like taffy for tendrils."
        )

    def brush_draw(
        self,
        object_name: Optional[str] = None,
        radius: float = 0.1,
        strength: float = 0.5,
    ) -> str:
        """
        Sets up Draw brush for basic sculpting.

        Basic sculpting - pushes/pulls surface.
        Essential for: general shaping, wrinkles, surface variation.
        """
        obj, previous_mode = self._ensure_sculpt_mode(object_name)

        # Clamp values
        radius = max(0.001, radius)
        strength = max(0.0, min(1.0, strength))

        # Get tool settings
        tool_settings = bpy.context.tool_settings
        sculpt = tool_settings.sculpt

        # Select draw brush
        bpy.ops.wm.tool_set_by_id(name="builtin_brush.Draw")

        # Configure brush settings
        brush = sculpt.brush
        if brush:
            brush.size = int(radius * 200)
            brush.strength = strength

        return (
            f"Draw brush ready on '{obj.name}' "
            f"(radius={radius}, strength={strength}). "
            f"Basic sculpting - pushes/pulls surface."
        )

    def brush_pinch(
        self,
        object_name: Optional[str] = None,
        radius: float = 0.1,
        strength: float = 0.5,
    ) -> str:
        """
        Sets up Pinch brush for pulling geometry toward center.

        Pulls geometry toward center - creates sharp creases.
        Essential for: wrinkles, folds, membrane attachments.
        """
        obj, previous_mode = self._ensure_sculpt_mode(object_name)

        # Clamp values
        radius = max(0.001, radius)
        strength = max(0.0, min(1.0, strength))

        # Get tool settings
        tool_settings = bpy.context.tool_settings
        sculpt = tool_settings.sculpt

        # Select pinch brush
        bpy.ops.wm.tool_set_by_id(name="builtin_brush.Pinch")

        # Configure brush settings
        brush = sculpt.brush
        if brush:
            brush.size = int(radius * 200)
            brush.strength = strength

        return (
            f"Pinch brush ready on '{obj.name}' "
            f"(radius={radius}, strength={strength}). "
            f"Pulls geometry toward center for creases."
        )

    # ==========================================================================
    # TASK-038-4: Dynamic Topology (Dyntopo)
    # ==========================================================================

    def enable_dyntopo(
        self,
        object_name: Optional[str] = None,
        detail_mode: str = "RELATIVE",
        detail_size: float = 12.0,
        use_smooth_shading: bool = True,
    ) -> str:
        """
        Enables Dynamic Topology for automatic geometry addition.

        Dyntopo automatically adds/removes geometry as you sculpt.
        No need to worry about base mesh topology.

        Warning: Destroys UV maps and vertex groups.
        """
        obj, previous_mode = self._ensure_sculpt_mode(object_name)

        # Validate detail mode
        valid_modes = ["RELATIVE", "CONSTANT", "BRUSH", "MANUAL"]
        detail_mode = detail_mode.upper()
        if detail_mode not in valid_modes:
            raise ValueError(f"Invalid detail mode: {detail_mode}. Valid: {valid_modes}")

        # Enable dynamic topology
        sculpt = bpy.context.tool_settings.sculpt

        # Check if dyntopo is already enabled
        if not bpy.context.sculpt_object.use_dynamic_topology_sculpting:
            bpy.ops.sculpt.dynamic_topology_toggle()

        # Set detail mode
        sculpt.detail_type_method = detail_mode

        # Set detail size based on mode
        if detail_mode == "RELATIVE":
            sculpt.detail_size = detail_size  # Pixels
        elif detail_mode == "CONSTANT":
            sculpt.constant_detail_resolution = detail_size  # Blender units (inverted)
        elif detail_mode == "BRUSH":
            sculpt.detail_percent = detail_size  # Percentage

        # Set shading
        if use_smooth_shading:
            bpy.ops.mesh.faces_shade_smooth()

        return (
            f"Dynamic Topology enabled on '{obj.name}' "
            f"(mode={detail_mode}, detail={detail_size}, smooth={use_smooth_shading}). "
            f"Warning: UVs and vertex groups will be destroyed."
        )

    def disable_dyntopo(
        self,
        object_name: Optional[str] = None,
    ) -> str:
        """
        Disables Dynamic Topology.

        After disabling, consider mesh_remesh_voxel for clean topology.
        """
        obj, previous_mode = self._ensure_sculpt_mode(object_name)

        # Check if dyntopo is enabled
        if bpy.context.sculpt_object.use_dynamic_topology_sculpting:
            bpy.ops.sculpt.dynamic_topology_toggle()
            return f"Dynamic Topology disabled on '{obj.name}'. Consider mesh_remesh_voxel for clean topology."
        else:
            return f"Dynamic Topology was not enabled on '{obj.name}'."

    def dyntopo_flood_fill(
        self,
        object_name: Optional[str] = None,
    ) -> str:
        """
        Applies current detail level to entire mesh.

        Useful for: unifying detail level after sculpting.
        """
        obj, previous_mode = self._ensure_sculpt_mode(object_name)

        # Check if dyntopo is enabled
        if not bpy.context.sculpt_object.use_dynamic_topology_sculpting:
            raise ValueError(f"Dynamic Topology is not enabled on '{obj.name}'. Enable it first with enable_dyntopo().")

        # Flood fill detail
        bpy.ops.sculpt.detail_flood_fill()

        return f"Applied current detail level to entire mesh '{obj.name}'."
