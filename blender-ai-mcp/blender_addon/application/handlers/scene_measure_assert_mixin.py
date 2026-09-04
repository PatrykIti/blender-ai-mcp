import bpy


class SceneMeasureAssertMixin:
    """Measurement and assertion helpers for scene RPC methods."""

    def measure_distance(self, from_object, to_object, reference="ORIGIN"):
        """Measures distance between two objects using one reference point mode."""
        import math

        source = self._get_object_or_raise(from_object)
        target = self._get_object_or_raise(to_object)

        reference_mode = str(reference).upper()
        if reference_mode == "ORIGIN":
            source_point = [float(source.location[i]) for i in range(3)]
            target_point = [float(target.location[i]) for i in range(3)]
        elif reference_mode == "BBOX_CENTER":
            source_point = self._get_bbox_data(source, world_space=True)["center"]
            target_point = self._get_bbox_data(target, world_space=True)["center"]
        else:
            raise ValueError("reference must be ORIGIN or BBOX_CENTER")

        delta = [target_point[i] - source_point[i] for i in range(3)]
        distance = math.sqrt(sum(value * value for value in delta))

        return {
            "from_object": from_object,
            "to_object": to_object,
            "reference": reference_mode,
            "distance": round(float(distance), 6),
            "delta": self._round_values(delta),
            "from_point": self._round_values(source_point),
            "to_point": self._round_values(target_point),
            "units": "blender_units",
        }

    def measure_dimensions(self, object_name, world_space=True):
        """Measures object dimensions in Blender units."""
        bbox_data = self._get_bbox_data(self._get_object_or_raise(object_name), world_space=world_space)
        dimensions = bbox_data["dimensions"]
        volume = dimensions[0] * dimensions[1] * dimensions[2]

        return {
            "object_name": object_name,
            "world_space": world_space,
            "dimensions": self._round_values(dimensions),
            "volume": round(float(volume), 6),
            "units": "blender_units",
        }

    def measure_gap(self, from_object, to_object, tolerance=0.0001):
        """Measures the nearest gap/contact state between two objects."""
        import math

        source_obj = self._get_object_or_raise(from_object)
        target_obj = self._get_object_or_raise(to_object)
        source_bbox = self._get_bbox_data(source_obj, world_space=True)
        target_bbox = self._get_bbox_data(target_obj, world_space=True)

        axis_gap = [
            self._axis_gap(
                source_bbox["min"][axis_index],
                source_bbox["max"][axis_index],
                target_bbox["min"][axis_index],
                target_bbox["max"][axis_index],
            )
            for axis_index in range(3)
        ]
        overlap_dimensions = [
            self._axis_overlap(
                source_bbox["min"][axis_index],
                source_bbox["max"][axis_index],
                target_bbox["min"][axis_index],
                target_bbox["max"][axis_index],
            )
            for axis_index in range(3)
        ]
        gap_distance = math.sqrt(sum(value * value for value in axis_gap))

        if gap_distance > tolerance:
            bbox_relation = "separated"
        elif all(value > tolerance for value in overlap_dimensions):
            bbox_relation = "overlapping"
        else:
            bbox_relation = "contact"

        bbox_overlap_volume = 0.0
        if bbox_relation == "overlapping":
            bbox_overlap_volume = overlap_dimensions[0] * overlap_dimensions[1] * overlap_dimensions[2]

        mesh_contact = self._measure_mesh_surface_relation(
            source_obj,
            target_obj,
            tolerance,
            bbox_overlap_volume=bbox_overlap_volume,
        )
        if mesh_contact is not None:
            return {
                "from_object": from_object,
                "to_object": to_object,
                "gap": round(float(mesh_contact["gap"]), 6),
                "axis_gap": self._round_axis_mapping(mesh_contact["axis_gap"]),
                "relation": mesh_contact["relation"],
                "tolerance": round(float(tolerance), 6),
                "units": "blender_units",
                "measurement_basis": "mesh_surface",
                "bbox_gap": round(float(gap_distance), 6),
                "bbox_axis_gap": self._round_axis_mapping(axis_gap),
                "bbox_relation": bbox_relation,
                "nearest_points": mesh_contact["nearest_points"],
            }

        return {
            "from_object": from_object,
            "to_object": to_object,
            "gap": round(float(gap_distance), 6),
            "axis_gap": self._round_axis_mapping(axis_gap),
            "relation": bbox_relation,
            "tolerance": round(float(tolerance), 6),
            "units": "blender_units",
            "measurement_basis": "bounding_box",
        }

    def measure_alignment(self, from_object, to_object, axes=None, reference="CENTER", tolerance=0.0001):
        """Measures object alignment across one or more axes."""
        source_bbox = self._get_bbox_data(self._get_object_or_raise(from_object), world_space=True)
        target_bbox = self._get_bbox_data(self._get_object_or_raise(to_object), world_space=True)

        normalized_axes = self._normalize_axes(axes)
        reference_mode = str(reference).upper()
        if reference_mode not in {"CENTER", "MIN", "MAX"}:
            raise ValueError("reference must be CENTER, MIN, or MAX")

        point_key = {"CENTER": "center", "MIN": "min", "MAX": "max"}[reference_mode]
        axis_indices = {"X": 0, "Y": 1, "Z": 2}
        delta_map = {
            axis.lower(): round(
                float(target_bbox[point_key][axis_indices[axis]] - source_bbox[point_key][axis_indices[axis]]), 6
            )
            for axis in normalized_axes
        }
        aligned_axes = [axis for axis in normalized_axes if abs(delta_map[axis.lower()]) <= tolerance]
        misaligned_axes = [axis for axis in normalized_axes if axis not in aligned_axes]
        max_abs_delta = max((abs(delta_map[axis.lower()]) for axis in normalized_axes), default=0.0)

        return {
            "from_object": from_object,
            "to_object": to_object,
            "reference": reference_mode,
            "axes": normalized_axes,
            "deltas": delta_map,
            "aligned_axes": aligned_axes,
            "misaligned_axes": misaligned_axes,
            "is_aligned": len(aligned_axes) == len(normalized_axes),
            "max_abs_delta": round(float(max_abs_delta), 6),
            "tolerance": round(float(tolerance), 6),
            "units": "blender_units",
        }

    def measure_overlap(self, from_object, to_object, tolerance=0.0001):
        """Measures overlap/intersection between two objects."""
        source_obj = self._get_object_or_raise(from_object)
        target_obj = self._get_object_or_raise(to_object)
        source_bbox = self._get_bbox_data(source_obj, world_space=True)
        target_bbox = self._get_bbox_data(target_obj, world_space=True)

        intersection_min = [
            max(source_bbox["min"][axis_index], target_bbox["min"][axis_index]) for axis_index in range(3)
        ]
        intersection_max = [
            min(source_bbox["max"][axis_index], target_bbox["max"][axis_index]) for axis_index in range(3)
        ]
        overlap_dimensions = [
            max(0.0, intersection_max[axis_index] - intersection_min[axis_index]) for axis_index in range(3)
        ]
        bbox_overlaps = all(value > tolerance for value in overlap_dimensions)
        gap_axes = [
            self._axis_gap(
                source_bbox["min"][axis_index],
                source_bbox["max"][axis_index],
                target_bbox["min"][axis_index],
                target_bbox["max"][axis_index],
            )
            for axis_index in range(3)
        ]
        bbox_touching = not bbox_overlaps and all(value <= tolerance for value in gap_axes)
        bbox_overlap_volume = 0.0
        if bbox_overlaps:
            bbox_overlap_volume = overlap_dimensions[0] * overlap_dimensions[1] * overlap_dimensions[2]

        if bbox_overlaps:
            bbox_relation = "overlap"
        elif bbox_touching:
            bbox_relation = "touching"
        else:
            bbox_relation = "disjoint"

        mesh_contact = self._measure_mesh_surface_relation(
            source_obj,
            target_obj,
            tolerance,
            bbox_overlap_volume=bbox_overlap_volume,
        )
        if mesh_contact is not None:
            overlaps = bool(mesh_contact["overlaps"])
            touching = mesh_contact["relation"] == "contact"
            if overlaps:
                relation = "overlap"
            elif touching:
                relation = "touching"
            else:
                relation = "disjoint"
            return {
                "from_object": from_object,
                "to_object": to_object,
                "overlaps": overlaps,
                "touching": touching,
                "relation": relation,
                "overlap_dimensions": self._round_values(overlap_dimensions if overlaps else [0.0, 0.0, 0.0]),
                "overlap_volume": round(float(bbox_overlap_volume if overlaps else 0.0), 6),
                "intersection_min": self._round_values(intersection_min) if overlaps else None,
                "intersection_max": self._round_values(intersection_max) if overlaps else None,
                "tolerance": round(float(tolerance), 6),
                "units": "blender_units",
                "measurement_basis": "mesh_surface",
                "surface_gap": round(float(mesh_contact["gap"]), 6),
                "bbox_relation": bbox_relation,
                "bbox_touching": bbox_touching,
                "bbox_overlap_dimensions": self._round_values(overlap_dimensions),
                "bbox_overlap_volume": round(float(bbox_overlap_volume), 6),
                "nearest_points": mesh_contact["nearest_points"],
            }

        return {
            "from_object": from_object,
            "to_object": to_object,
            "overlaps": bbox_overlaps,
            "touching": bbox_touching,
            "relation": bbox_relation,
            "overlap_dimensions": self._round_values(overlap_dimensions),
            "overlap_volume": round(float(bbox_overlap_volume), 6),
            "intersection_min": self._round_values(intersection_min) if bbox_overlaps else None,
            "intersection_max": self._round_values(intersection_max) if bbox_overlaps else None,
            "tolerance": round(float(tolerance), 6),
            "units": "blender_units",
            "measurement_basis": "bounding_box",
        }

    def assert_contact(self, from_object, to_object, max_gap=0.0001, allow_overlap=False):
        """Asserts the expected contact relation between two objects."""
        gap_result = self.measure_gap(from_object, to_object, tolerance=max_gap)
        relation = str(gap_result["relation"])
        gap = float(gap_result["gap"])
        overlaps = relation == "overlapping"
        passed = gap <= max_gap and (allow_overlap or not overlaps)
        gap_overage = max(0.0, gap - max_gap)

        return self._build_assertion_payload(
            assertion="scene_assert_contact",
            subject=from_object,
            target=to_object,
            passed=passed,
            expected={
                "max_gap": round(float(max_gap), 6),
                "allow_overlap": bool(allow_overlap),
            },
            actual={
                "gap": round(float(gap), 6),
                "relation": relation,
            },
            delta={"gap_overage": round(float(gap_overage), 6)},
            tolerance=max_gap,
            units="blender_units",
            details={
                "axis_gap": gap_result["axis_gap"],
                "measured_relation": relation,
                "overlap_rejected": overlaps and not allow_overlap,
                "measurement_basis": gap_result.get("measurement_basis", "bounding_box"),
                "bbox_relation": gap_result.get("bbox_relation"),
                "nearest_points": gap_result.get("nearest_points"),
            },
        )

    def assert_dimensions(self, object_name, expected_dimensions, tolerance=0.0001, world_space=True):
        """Asserts that object dimensions match the expected vector within tolerance."""
        if expected_dimensions is None or len(expected_dimensions) != 3:
            raise ValueError("expected_dimensions must contain exactly 3 values")

        measurement = self.measure_dimensions(object_name, world_space=world_space)
        actual_dimensions = [float(value) for value in measurement["dimensions"]]
        expected = [float(value) for value in expected_dimensions]
        delta = [actual_dimensions[index] - expected[index] for index in range(3)]
        axis_delta = self._round_axis_mapping(delta)
        passed_axes = [axis for axis in ("x", "y", "z") if abs(axis_delta[axis]) <= tolerance]
        failed_axes = [axis.upper() for axis in ("x", "y", "z") if axis not in passed_axes]

        return self._build_assertion_payload(
            assertion="scene_assert_dimensions",
            subject=object_name,
            passed=len(failed_axes) == 0,
            expected={"dimensions": self._round_values(expected)},
            actual={"dimensions": self._round_values(actual_dimensions)},
            delta=axis_delta,
            tolerance=tolerance,
            units="blender_units",
            details={
                "world_space": bool(world_space),
                "passed_axes": [axis.upper() for axis in passed_axes],
                "failed_axes": failed_axes,
            },
        )

    def assert_containment(self, inner_object, outer_object, min_clearance=0.0, tolerance=0.0001):
        """Asserts that one object is contained within another."""
        inner_bbox = self._get_bbox_data(self._get_object_or_raise(inner_object), world_space=True)
        outer_bbox = self._get_bbox_data(self._get_object_or_raise(outer_object), world_space=True)

        axis_clearances = {}
        protruding_axes = []
        min_axis_clearance = None
        max_protrusion = 0.0

        for axis, index in self._axis_indices().items():
            lower_clearance = inner_bbox["min"][index] - outer_bbox["min"][index]
            upper_clearance = outer_bbox["max"][index] - inner_bbox["max"][index]
            axis_clearance = min(lower_clearance, upper_clearance)
            axis_clearances[axis.lower()] = round(float(axis_clearance), 6)
            if axis_clearance < -tolerance:
                protruding_axes.append(axis)
                max_protrusion = max(max_protrusion, abs(float(axis_clearance)))
            if min_axis_clearance is None:
                min_axis_clearance = axis_clearance
            else:
                min_axis_clearance = min(min_axis_clearance, axis_clearance)

        min_axis_clearance = float(min_axis_clearance or 0.0)
        clearance_shortfall = max(0.0, min_clearance - min_axis_clearance)
        passed = not protruding_axes and clearance_shortfall <= tolerance

        return self._build_assertion_payload(
            assertion="scene_assert_containment",
            subject=inner_object,
            target=outer_object,
            passed=passed,
            expected={"min_clearance": round(float(min_clearance), 6)},
            actual={"min_clearance": round(float(min_axis_clearance), 6)},
            delta={
                "clearance_shortfall": round(float(clearance_shortfall), 6),
                "max_protrusion": round(float(max_protrusion), 6),
            },
            tolerance=tolerance,
            units="blender_units",
            details={
                "axis_clearance": axis_clearances,
                "protruding_axes": protruding_axes,
            },
        )

    def assert_symmetry(self, left_object, right_object, axis="X", mirror_coordinate=0.0, tolerance=0.0001):
        """Asserts symmetry between two objects across a mirror plane."""
        axis_name = self._normalize_axis(axis, parameter_name="axis")
        axis_index = self._axis_indices()[axis_name]
        left_bbox = self._get_bbox_data(self._get_object_or_raise(left_object), world_space=True)
        right_bbox = self._get_bbox_data(self._get_object_or_raise(right_object), world_space=True)

        expected_right_axis = (2.0 * float(mirror_coordinate)) - float(left_bbox["center"][axis_index])
        center_deltas = {}
        dimension_deltas = {}
        failed_checks = []

        for candidate_axis, index in self._axis_indices().items():
            if index == axis_index:
                continue
            delta = float(right_bbox["center"][index] - left_bbox["center"][index])
            center_deltas[candidate_axis.lower()] = round(delta, 6)
            if abs(delta) > tolerance:
                failed_checks.append(f"center_{candidate_axis.lower()}")

        for candidate_axis, index in self._axis_indices().items():
            delta = float(right_bbox["dimensions"][index] - left_bbox["dimensions"][index])
            dimension_deltas[candidate_axis.lower()] = round(delta, 6)
            if abs(delta) > tolerance:
                failed_checks.append(f"dimensions_{candidate_axis.lower()}")

        mirror_delta = float(right_bbox["center"][axis_index] - expected_right_axis)
        if abs(mirror_delta) > tolerance:
            failed_checks.append(f"mirror_{axis_name.lower()}")

        return self._build_assertion_payload(
            assertion="scene_assert_symmetry",
            subject=left_object,
            target=right_object,
            passed=len(failed_checks) == 0,
            expected={"axis": axis_name, "mirror_coordinate": round(float(mirror_coordinate), 6)},
            actual={
                "left_center": self._round_values(left_bbox["center"]),
                "right_center": self._round_values(right_bbox["center"]),
                "left_dimensions": self._round_values(left_bbox["dimensions"]),
                "right_dimensions": self._round_values(right_bbox["dimensions"]),
            },
            delta={
                "mirror_axis": round(mirror_delta, 6),
                "center": center_deltas,
                "dimensions": dimension_deltas,
            },
            tolerance=tolerance,
            units="blender_units",
            details={"failed_checks": failed_checks},
        )

    def assert_proportion(
        self,
        object_name,
        axis_a,
        expected_ratio,
        axis_b=None,
        reference_object=None,
        reference_axis=None,
        tolerance=0.01,
        world_space=True,
    ):
        """Asserts one ratio/proportion against the expected value."""
        axis_a_name = self._normalize_axis(axis_a, parameter_name="axis_a")
        axis_a_index = self._axis_indices()[axis_a_name]

        if axis_b is not None and (reference_object is not None or reference_axis is not None):
            raise ValueError("Use either axis_b or reference_object/reference_axis, not both")
        if axis_b is None and (reference_object is None or reference_axis is None):
            raise ValueError("Provide either axis_b or both reference_object and reference_axis")

        source_bbox = self._get_bbox_data(self._get_object_or_raise(object_name), world_space=world_space)
        numerator = float(source_bbox["dimensions"][axis_a_index])

        if axis_b is not None:
            axis_b_name = self._normalize_axis(axis_b, parameter_name="axis_b")
            denominator = float(source_bbox["dimensions"][self._axis_indices()[axis_b_name]])
            mode = "single_object"
            target_name = object_name
            proportion_target = {"axis_b": axis_b_name}
        else:
            reference_axis_name = self._normalize_axis(reference_axis, parameter_name="reference_axis")
            reference_bbox = self._get_bbox_data(self._get_object_or_raise(reference_object), world_space=world_space)
            denominator = float(reference_bbox["dimensions"][self._axis_indices()[reference_axis_name]])
            mode = "cross_object"
            target_name = reference_object
            proportion_target = {
                "reference_object": reference_object,
                "reference_axis": reference_axis_name,
            }

        if abs(denominator) < 1e-9:
            raise ValueError("Proportion denominator is zero; cannot compute ratio")

        actual_ratio = numerator / denominator
        ratio_delta = float(actual_ratio - expected_ratio)

        return self._build_assertion_payload(
            assertion="scene_assert_proportion",
            subject=object_name,
            target=target_name,
            passed=abs(ratio_delta) <= tolerance,
            expected={
                "ratio": round(float(expected_ratio), 6),
                "axis_a": axis_a_name,
                **proportion_target,
            },
            actual={"ratio": round(float(actual_ratio), 6), "mode": mode},
            delta={"ratio_delta": round(float(ratio_delta), 6)},
            tolerance=tolerance,
            units="ratio",
            details={"world_space": bool(world_space)},
        )

    def _get_evaluated_mesh_data(self, obj):
        """Returns evaluated world-space mesh data for mesh-aware truth checks."""

        if getattr(obj, "type", None) != "MESH":
            return None

        obj_eval = None
        release_evaluated_mesh = False
        try:
            depsgraph = bpy.context.evaluated_depsgraph_get()
            obj_eval = obj.evaluated_get(depsgraph)
            mesh = obj_eval.to_mesh()
            release_evaluated_mesh = True
        except Exception:
            return None

        try:
            world_vertices = [obj_eval.matrix_world @ vertex.co for vertex in getattr(mesh, "vertices", [])]
            if not world_vertices:
                return None
            try:
                mesh.calc_loop_triangles()
            except Exception:
                pass
            triangles = [tuple(tri.vertices) for tri in getattr(mesh, "loop_triangles", []) if len(tri.vertices) == 3]
            if not triangles:
                return None
            polygon_centers = [obj_eval.matrix_world @ poly.center for poly in getattr(mesh, "polygons", [])]
            release_evaluated_mesh = False
            return {
                "object_name": obj.name,
                "vertices": world_vertices,
                "triangles": triangles,
                "sample_points": [*world_vertices, *polygon_centers],
                "cleanup_owner": obj_eval,
            }
        except Exception:
            return None
        finally:
            if release_evaluated_mesh and hasattr(obj_eval, "to_mesh_clear"):
                try:
                    obj_eval.to_mesh_clear()
                except Exception:
                    pass

    def _release_evaluated_mesh_data(self, mesh_data):
        """Releases temporary evaluated mesh data created for mesh-aware checks."""

        if not isinstance(mesh_data, dict):
            return
        cleanup_owner = mesh_data.get("cleanup_owner")
        if hasattr(cleanup_owner, "to_mesh_clear"):
            try:
                cleanup_owner.to_mesh_clear()
            except Exception:
                pass

    def _find_closest_surface_pair(self, sample_points, target_tree, tolerance):
        """Find the closest sampled surface point against a target BVH tree."""

        best_pair = None
        best_distance = None
        for point in sample_points:
            try:
                nearest = target_tree.find_nearest(point)
            except Exception:
                continue
            if not nearest or nearest[0] is None or nearest[3] is None:
                continue
            nearest_point, _normal, _index, distance = nearest
            if best_distance is None or float(distance) < best_distance:
                best_distance = float(distance)
                best_pair = (point, nearest_point)
                if best_distance <= tolerance:
                    break
        return best_pair, best_distance

    def _has_effectively_zero_bbox_dimension(self, obj, tolerance):
        """Return True when the object's local bbox collapses on at least one axis."""

        try:
            bbox = list(getattr(obj, "bound_box", ()) or ())
            if not bbox:
                return False
            minima = [min(float(corner[axis_index]) for corner in bbox) for axis_index in range(3)]
            maxima = [max(float(corner[axis_index]) for corner in bbox) for axis_index in range(3)]
            return any(abs(maxima[axis_index] - minima[axis_index]) <= float(tolerance) for axis_index in range(3))
        except Exception:
            return False

    def _measure_mesh_surface_relation(self, source_obj, target_obj, tolerance, bbox_overlap_volume=0.0):
        """Returns mesh-aware contact/gap semantics for mesh-object pairs when possible."""

        try:
            from mathutils.bvhtree import BVHTree
        except Exception:
            return None

        source_mesh = self._get_evaluated_mesh_data(source_obj)
        target_mesh = self._get_evaluated_mesh_data(target_obj)
        if source_mesh is None or target_mesh is None:
            self._release_evaluated_mesh_data(source_mesh)
            self._release_evaluated_mesh_data(target_mesh)
            return None

        try:
            source_tree = BVHTree.FromPolygons(source_mesh["vertices"], source_mesh["triangles"], all_triangles=True)
            target_tree = BVHTree.FromPolygons(target_mesh["vertices"], target_mesh["triangles"], all_triangles=True)
            if source_tree is None or target_tree is None:
                return None

            overlap_pairs = source_tree.overlap(target_tree)
            overlap_volume_threshold = max(float(tolerance) ** 3, 1e-12)
            zero_thickness_overlap = bool(overlap_pairs) and (
                self._has_effectively_zero_bbox_dimension(source_obj, tolerance)
                or self._has_effectively_zero_bbox_dimension(target_obj, tolerance)
            )
            overlaps = bool(overlap_pairs) and (
                float(bbox_overlap_volume) > overlap_volume_threshold or zero_thickness_overlap
            )
            if overlaps:
                return {
                    "overlaps": True,
                    "gap": 0.0,
                    "axis_gap": [0.0, 0.0, 0.0],
                    "relation": "overlapping",
                    "nearest_points": None,
                }

            source_pair, source_distance = self._find_closest_surface_pair(
                source_mesh["sample_points"], target_tree, tolerance
            )
            target_pair, target_distance = self._find_closest_surface_pair(
                target_mesh["sample_points"], source_tree, tolerance
            )
            candidates = [
                (source_pair, source_distance),
                (
                    (target_pair[1], target_pair[0]) if target_pair is not None else None,
                    target_distance,
                ),
            ]
            valid_candidates = [
                (pair, distance) for pair, distance in candidates if pair is not None and distance is not None
            ]
            if not valid_candidates:
                return None

            best_pair, best_distance = min(valid_candidates, key=lambda item: float(item[1]))
            point_a, point_b = best_pair
            axis_gap = [abs(float(point_b[index]) - float(point_a[index])) for index in range(3)]
            relation = "contact" if float(best_distance) <= tolerance else "separated"
            return {
                "overlaps": False,
                "gap": round(float(best_distance), 6),
                "axis_gap": axis_gap,
                "relation": relation,
                "nearest_points": {
                    "from_object": self._round_values(point_a),
                    "to_object": self._round_values(point_b),
                },
            }
        finally:
            self._release_evaluated_mesh_data(source_mesh)
            self._release_evaluated_mesh_data(target_mesh)

    def _normalize_axes(self, axes):
        """Normalizes axis list input for alignment measurements."""
        if axes is None:
            return ["X", "Y", "Z"]

        normalized = [str(axis).upper() for axis in axes]
        invalid = [axis for axis in normalized if axis not in {"X", "Y", "Z"}]
        if invalid:
            invalid_axes = ", ".join(sorted(set(invalid)))
            raise ValueError(f"axes must contain only X, Y, or Z. Invalid values: {invalid_axes}")
        if not normalized:
            raise ValueError("axes must contain at least one axis")
        return normalized

    def _axis_gap(self, source_min, source_max, target_min, target_max):
        """Returns the positive separation between intervals on one axis."""
        if source_max < target_min:
            return float(target_min - source_max)
        if target_max < source_min:
            return float(source_min - target_max)
        return 0.0

    def _axis_overlap(self, source_min, source_max, target_min, target_max):
        """Returns the overlap depth between intervals on one axis."""
        return max(0.0, float(min(source_max, target_max) - max(source_min, target_min)))

    def _round_axis_mapping(self, values, precision=6):
        """Rounds XYZ values into an axis-keyed dictionary."""
        return {
            "x": round(float(values[0]), precision),
            "y": round(float(values[1]), precision),
            "z": round(float(values[2]), precision),
        }

    def _axis_indices(self):
        """Returns the canonical axis index mapping."""
        return {"X": 0, "Y": 1, "Z": 2}

    def _normalize_axis(self, axis, parameter_name="axis"):
        """Normalizes one axis input and raises a clear error when invalid."""
        axis_name = str(axis).upper()
        if axis_name not in self._axis_indices():
            raise ValueError(f"{parameter_name} must be one of X, Y, or Z")
        return axis_name

    def _build_assertion_payload(
        self,
        *,
        assertion,
        subject,
        passed,
        target=None,
        expected=None,
        actual=None,
        delta=None,
        tolerance=None,
        units=None,
        details=None,
    ):
        """Builds a compact shared payload for scene assertion tools."""
        payload = {
            "assertion": assertion,
            "passed": bool(passed),
            "subject": subject,
            "target": target,
            "expected": expected,
            "actual": actual,
            "delta": delta,
            "tolerance": round(float(tolerance), 6) if tolerance is not None else None,
            "units": units,
            "details": details,
        }
        return {key: value for key, value in payload.items() if value is not None}
