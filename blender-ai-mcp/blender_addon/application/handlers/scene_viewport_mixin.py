import base64
import math
import os
import tempfile
from typing import Callable

import bpy

from .job_utils import raise_if_cancelled


class SceneViewportMixin:
    """Viewport, camera, and view-diagnostics helpers for scene RPC methods."""

    def get_viewport(
        self,
        width=1024,
        height=768,
        shading="SOLID",
        camera_name=None,
        focus_target=None,
        view_name=None,
        orbit_horizontal=0.0,
        orbit_vertical=0.0,
        zoom_factor=None,
        persist_view=False,
        progress_callback: Callable[[float, float | None, str | None], None] | None = None,
        is_cancelled: Callable[[], bool] | None = None,
    ):
        """Returns a base64 encoded OpenGL render of the viewport."""
        scene = bpy.context.scene
        raise_if_cancelled(is_cancelled)
        if progress_callback is not None:
            progress_callback(0, 1, "Preparing viewport capture")

        # 0. Ensure Object Mode (Safety check for render operators)
        original_mode = None
        if bpy.context.active_object:
            original_mode = bpy.context.active_object.mode
            if original_mode != "OBJECT":
                try:
                    bpy.ops.object.mode_set(mode="OBJECT")
                except Exception:
                    pass

        # Create a dedicated temp directory for this render to avoid filename collisions
        temp_dir = tempfile.mkdtemp()
        # Define the output path. Blender will append extensions based on format.
        # We force JPEG.
        render_filename = "viewport_render"
        render_filepath_base = os.path.join(temp_dir, render_filename)
        # Expected output file (Blender adds extension)
        expected_output = render_filepath_base + ".jpg"

        try:
            # 1. Locate 3D View for context overrides (Used for OpenGL)
            view_area = None
            view_space = None
            view_region = None

            for area in bpy.context.screen.areas:
                if area.type == "VIEW_3D":
                    view_area = area
                    for space in area.spaces:
                        if space.type == "VIEW_3D":
                            view_space = space
                    for region in area.regions:
                        if region.type == "WINDOW":
                            view_region = region
                    break

            # 2. Save State
            original_res_x = scene.render.resolution_x
            original_res_y = scene.render.resolution_y
            original_filepath = scene.render.filepath
            original_camera = scene.camera
            original_engine = scene.render.engine
            original_file_format = scene.render.image_settings.file_format
            original_view_state = None

            if view_space:
                original_shading_type = view_space.shading.type
                try:
                    original_view_state = self.get_view_state()
                except Exception:
                    original_view_state = None

            original_active = bpy.context.view_layer.objects.active
            original_selected = [obj for obj in bpy.context.view_layer.objects if obj.select_get()]

            # 3. Setup Render Settings
            scene.render.resolution_x = width
            scene.render.resolution_y = height
            scene.render.image_settings.file_format = "JPEG"
            scene.render.filepath = render_filepath_base

            # 4. Apply Shading (for OpenGL/Workbench)
            # Validate shading type
            valid_shading = {"WIREFRAME", "SOLID", "MATERIAL", "RENDERED"}
            target_shading = shading.upper() if shading.upper() in valid_shading else "SOLID"

            if view_space:
                view_space.shading.type = target_shading

            # 5. Handle Camera & Focus
            temp_camera_obj = None
            use_explicit_scene_camera = bool(camera_name and camera_name != "USER_PERSPECTIVE")
            view_name_value = str(view_name).upper() if view_name is not None else None
            zoom_value = float(zoom_factor) if zoom_factor is not None else None
            orbit_h = float(orbit_horizontal or 0.0)
            orbit_v = float(orbit_vertical or 0.0)
            has_user_view_adjustment = bool(view_name_value or orbit_h or orbit_v or zoom_value is not None)
            user_view_state_mutated = False
            user_view_available = bool(view_space and view_area and view_region)

            try:
                # Case A: Specific existing camera
                if use_explicit_scene_camera:
                    if has_user_view_adjustment:
                        raise ValueError(
                            "view_name/orbit/zoom options are only supported with USER_PERSPECTIVE captures."
                        )
                    if camera_name in bpy.data.objects:
                        scene.camera = bpy.data.objects[camera_name]
                    else:
                        raise ValueError(f"Camera '{camera_name}' not found.")

                # Case B: Dynamic View (User Perspective)
                else:
                    if not user_view_available:
                        raise RuntimeError(
                            "USER_PERSPECTIVE capture requires an active 3D viewport. "
                            "Use an explicit camera_name for deterministic headless/background capture."
                        )

                    rv3d = view_space.region_3d if view_space else None
                    if view_name_value:
                        self.set_standard_view(view_name_value)
                        user_view_state_mutated = True

                    if focus_target:
                        self.camera_focus(focus_target, zoom_factor=zoom_value or 1.0)
                        user_view_state_mutated = True
                    elif zoom_value is not None:
                        if zoom_value <= 0:
                            raise ValueError("zoom_factor must be > 0")
                        if rv3d is not None:
                            rv3d.view_distance = float(rv3d.view_distance) / zoom_value
                            user_view_state_mutated = True

                    if orbit_h or orbit_v:
                        self.camera_orbit(
                            angle_horizontal=orbit_h,
                            angle_vertical=orbit_v,
                            target_object=focus_target,
                        )
                        user_view_state_mutated = True

                # 6. Render Strategy
                render_success = False

                # Strategy A: OpenGL Render (Fastest, requires Context)
                # Only attempt if we found a valid 3D View context and we are rendering
                # the live user perspective. Explicit camera renders should use the scene
                # camera path below so the image matches the named camera transform.
                if view_area and view_region and not use_explicit_scene_camera:
                    try:
                        with bpy.context.temp_override(area=view_area, region=view_region):
                            # write_still=True forces write to filepath
                            bpy.ops.render.opengl(write_still=True)

                        if os.path.exists(expected_output) and os.path.getsize(expected_output) > 0:
                            render_success = True
                    except Exception as e:
                        print(f"[Viewport] OpenGL render failed: {e}")

                # USER_PERSPECTIVE fallback path:
                # if OpenGL is unavailable/failed, mirror the current live 3D view into a
                # temporary camera so Workbench/Cycles still match what the user saw.
                if not render_success and not use_explicit_scene_camera:
                    bpy.ops.object.camera_add()
                    temp_camera_obj = bpy.context.active_object
                    scene.camera = temp_camera_obj

                    with bpy.context.temp_override(area=view_area, region=view_region):
                        bpy.ops.view3d.camera_to_view()

                # Strategy B: Workbench Render (Software Rasterization, Headless Safe)
                if not render_success:
                    print("[Viewport] Fallback to Workbench render...")
                    try:
                        scene.render.engine = "BLENDER_WORKBENCH"
                        # Configure Workbench to match requested style roughly
                        scene.display.shading.light = "STUDIO"
                        scene.display.shading.color_type = "MATERIAL"

                        if target_shading == "WIREFRAME":
                            # Workbench doesn't have direct "wireframe mode" global setting easily accessible via simple API in 4.0+
                            # without tweaking display settings, but rendering as is usually gives Solid.
                            # We can try to enable wireframe overlay if needed, but basic Workbench is usually SOLID.
                            pass

                        bpy.ops.render.render(write_still=True)

                        if os.path.exists(expected_output) and os.path.getsize(expected_output) > 0:
                            render_success = True
                    except Exception as e:
                        print(f"[Viewport] Workbench render failed: {e}")

                # Strategy C: Cycles (Ultimate Fallback, CPU Raytracing)
                if not render_success:
                    print("[Viewport] Fallback to Cycles render...")
                    try:
                        scene.render.engine = "CYCLES"
                        scene.cycles.device = "CPU"
                        scene.cycles.samples = 1  # Extremely fast, noisy but visible
                        scene.cycles.preview_samples = 1
                        bpy.ops.render.render(write_still=True)

                        if os.path.exists(expected_output) and os.path.getsize(expected_output) > 0:
                            render_success = True
                    except Exception as e:
                        print(f"[Viewport] Cycles render failed: {e}")

                # 7. Read Result
                if not render_success:
                    raise RuntimeError(
                        "Render failed: Could not generate viewport image using OpenGL, Workbench, or Cycles."
                    )
                raise_if_cancelled(is_cancelled)

                b64_data = ""
                with open(expected_output, "rb") as f:
                    data = f.read()
                    b64_data = base64.b64encode(data).decode("utf-8")
                if progress_callback is not None:
                    progress_callback(1, 1, "Viewport capture complete")

                return b64_data

            finally:
                # 8. Cleanup Temp Files
                if os.path.exists(expected_output):
                    os.remove(expected_output)
                try:
                    os.rmdir(temp_dir)
                except Exception:
                    pass

                # 9. Restore State
                scene.render.resolution_x = original_res_x
                scene.render.resolution_y = original_res_y
                scene.render.filepath = original_filepath
                scene.camera = original_camera
                scene.render.engine = original_engine
                scene.render.image_settings.file_format = original_file_format

                if view_space:
                    view_space.shading.type = original_shading_type

                if (
                    original_view_state
                    and not use_explicit_scene_camera
                    and not persist_view
                    and user_view_state_mutated
                ):
                    try:
                        self.restore_view_state(original_view_state)
                    except Exception:
                        pass

                # Restore selection
                bpy.ops.object.select_all(action="DESELECT")
                for obj in original_selected:
                    try:
                        obj.select_set(True)
                    except Exception:
                        pass

                if original_active and original_active.name in bpy.data.objects:
                    bpy.context.view_layer.objects.active = original_active

                # Cleanup temp camera
                if temp_camera_obj:
                    bpy.data.objects.remove(temp_camera_obj, do_unlink=True)
        finally:
            # 10. Restore Mode
            if original_mode and original_mode != "OBJECT":
                if bpy.context.active_object:
                    try:
                        bpy.ops.object.mode_set(mode=original_mode)
                    except Exception:
                        pass

    # TASK-043: Scene Utility Tools
    def camera_orbit(self, angle_horizontal=0.0, angle_vertical=0.0, target_object=None, target_point=None):
        """Orbits viewport camera around target."""
        from mathutils import Matrix, Vector

        # Get orbit center
        if target_object:
            obj = bpy.data.objects.get(target_object)
            if not obj:
                raise ValueError(f"Object '{target_object}' not found")
            center = obj.location.copy()
        elif target_point:
            center = Vector(target_point)
        else:
            center = Vector((0, 0, 0))

        # Find 3D viewport
        rv3d = None

        for area in bpy.context.screen.areas:
            if area.type == "VIEW_3D":
                for space in area.spaces:
                    if space.type == "VIEW_3D":
                        rv3d = space.region_3d
                        break
                break

        if not rv3d:
            return "No 3D viewport found. Camera orbit requires an active 3D view."

        # Convert degrees to radians
        h_rad = math.radians(angle_horizontal)
        v_rad = math.radians(angle_vertical)

        # Apply rotation to view
        # Horizontal rotation (around Z axis)
        rot_h = Matrix.Rotation(h_rad, 4, "Z")
        # Vertical rotation (around local X axis)
        rot_v = Matrix.Rotation(v_rad, 4, "X")

        # Combine rotations with existing view rotation
        rv3d.view_rotation = rv3d.view_rotation @ rot_h.to_quaternion()
        rv3d.view_rotation = rv3d.view_rotation @ rot_v.to_quaternion()

        # Set pivot point
        rv3d.view_location = center

        return f"Orbited viewport by {angle_horizontal}° horizontal, {angle_vertical}° vertical around {list(center)}"

    def camera_focus(self, object_name, zoom_factor=1.0):
        """Focuses viewport camera on object."""
        from mathutils import Vector

        obj = bpy.data.objects.get(object_name)
        if not obj:
            raise ValueError(f"Object '{object_name}' not found")

        # Find 3D viewport
        rv3d = None

        for area in bpy.context.screen.areas:
            if area.type == "VIEW_3D":
                for space in area.spaces:
                    if space.type == "VIEW_3D":
                        rv3d = space.region_3d
                        break
                break

        if not rv3d:
            return "No 3D viewport found. Camera focus requires an active 3D view."

        # Calculate object center and size from bounding box
        if obj.type == "MESH" and obj.data:
            # Get world-space bounding box
            bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
            center = sum(bbox_corners, Vector()) / 8

            # Calculate bounding sphere radius
            max_dist = max((corner - center).length for corner in bbox_corners)
            view_distance = max_dist * 2.5  # Add margin for framing
        else:
            # For non-mesh objects, use location and a default distance
            center = obj.location.copy()
            view_distance = 5.0

        # Set view location to object center
        rv3d.view_location = center

        # Set view distance (apply zoom factor)
        rv3d.view_distance = view_distance / zoom_factor

        # Also select the object for consistency
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        return f"Focused on '{object_name}' with zoom factor {zoom_factor}"

    def _find_view3d_context(self):
        view_area = None
        view_region = None
        view_space = None
        rv3d = None

        for area in getattr(bpy.context.screen, "areas", []):
            if getattr(area, "type", None) != "VIEW_3D":
                continue
            view_area = area
            for space in getattr(area, "spaces", []):
                if getattr(space, "type", None) == "VIEW_3D":
                    view_space = space
                    rv3d = getattr(space, "region_3d", None)
                    break
            for region in getattr(area, "regions", []):
                if getattr(region, "type", None) == "WINDOW":
                    view_region = region
                    break
            break

        return view_area, view_region, view_space, rv3d

    def _average_vectors(self, points):
        from mathutils import Vector

        if not points:
            return Vector((0.0, 0.0, 0.0))

        count = float(len(points))
        sums = [0.0, 0.0, 0.0]
        for point in points:
            sums[0] += float(point[0])
            sums[1] += float(point[1])
            sums[2] += float(point[2])
        return Vector((sums[0] / count, sums[1] / count, sums[2] / count))

    def _resolve_view_target_names(self, target_object=None, target_objects=None):
        names = []
        seen = set()
        for name in [target_object, *(target_objects or [])]:
            normalized = str(name or "").strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            names.append(normalized)
        return names

    def _project_point_to_camera(self, scene, camera_obj, point):
        try:
            from bpy_extras.object_utils import world_to_camera_view
        except Exception:
            return None

        try:
            projected = world_to_camera_view(scene, camera_obj, point)
            return {
                "x": float(getattr(projected, "x", projected[0])),
                "y": float(getattr(projected, "y", projected[1])),
                "z": float(getattr(projected, "z", projected[2])),
            }
        except Exception:
            return None

    def _object_bbox_points(self, obj):
        from mathutils import Vector

        bound_box = getattr(obj, "bound_box", None)
        matrix_world = getattr(obj, "matrix_world", None)
        if not bound_box or matrix_world is None:
            location = getattr(obj, "location", None)
            if location is None:
                return []
            try:
                return [location.copy()]
            except Exception:
                try:
                    return [Vector(location)]
                except Exception:
                    return []

        points = []
        for corner in bound_box:
            try:
                points.append(matrix_world @ Vector(corner))
            except Exception:
                continue
        return points

    def _object_view_sample_points(self, obj):
        from mathutils import Vector

        bbox_points = self._object_bbox_points(obj)
        if not bbox_points:
            return {"center": None, "projection_points": [], "visibility_points": []}

        center = self._average_vectors(bbox_points)
        x_values = [float(point[0]) for point in bbox_points]
        y_values = [float(point[1]) for point in bbox_points]
        z_values = [float(point[2]) for point in bbox_points]

        face_centers = [
            Vector((min(x_values), center[1], center[2])),
            Vector((max(x_values), center[1], center[2])),
            Vector((center[0], min(y_values), center[2])),
            Vector((center[0], max(y_values), center[2])),
            Vector((center[0], center[1], min(z_values))),
            Vector((center[0], center[1], max(z_values))),
        ]

        origin_point = None
        matrix_world = getattr(obj, "matrix_world", None)
        if matrix_world is not None:
            try:
                origin_point = matrix_world.translation.copy()
            except Exception:
                origin_point = None
        if origin_point is None:
            location = getattr(obj, "location", None)
            if location is not None:
                try:
                    origin_point = location.copy()
                except Exception:
                    try:
                        origin_point = Vector(location)
                    except Exception:
                        origin_point = None

        visibility_points = [center, *face_centers]
        if origin_point is not None and any((origin_point - point).length > 1e-6 for point in visibility_points):
            visibility_points.append(origin_point)

        return {
            "center": center,
            "projection_points": bbox_points,
            "visibility_points": visibility_points,
        }

    def _camera_ray_origin(self, camera_obj):
        matrix_world = getattr(camera_obj, "matrix_world", None)
        if matrix_world is None:
            return None
        try:
            return matrix_world.translation.copy()
        except Exception:
            return None

    def _target_visible_from_camera(self, scene, camera_obj, target_obj, point):
        origin = self._camera_ray_origin(camera_obj)
        if origin is None:
            return None

        try:
            depsgraph = bpy.context.evaluated_depsgraph_get()
        except Exception:
            return None

        try:
            direction = point - origin
            distance = float(direction.length)
        except Exception:
            return None
        if distance <= 1e-6:
            return True

        try:
            direction.normalize()
        except Exception:
            return None

        try:
            hit, _location, _normal, _index, hit_object, _matrix = scene.ray_cast(
                depsgraph,
                origin,
                direction,
                distance=distance + 1e-5,
            )
        except Exception:
            return None

        if not hit:
            return None

        current = hit_object
        while current is not None:
            if getattr(current, "name", None) == getattr(target_obj, "name", None):
                return True
            current = getattr(current, "parent", None)

        return False

    def _clamp_unit(self, value):
        return max(0.0, min(1.0, float(value)))

    def _build_view_target_diagnostic(self, scene, camera_obj, obj):
        sample_payload = self._object_view_sample_points(obj)
        center = sample_payload["center"]
        projection_points = sample_payload["projection_points"]
        visibility_points = sample_payload["visibility_points"]

        if center is None or not projection_points:
            return {
                "object_name": obj.name,
                "visibility_verdict": "unavailable",
                "projection_status": "unavailable",
                "unavailable_reason": "projection_points_unavailable",
            }

        projected_center = self._project_point_to_camera(scene, camera_obj, center)
        projected_bbox = [self._project_point_to_camera(scene, camera_obj, point) for point in projection_points]
        projected_bbox = [item for item in projected_bbox if item is not None]
        if projected_center is None or not projected_bbox:
            return {
                "object_name": obj.name,
                "visibility_verdict": "unavailable",
                "projection_status": "unavailable",
                "unavailable_reason": "projection_unavailable",
            }

        in_front_bbox = [item for item in projected_bbox if float(item["z"]) >= 0.0]
        if not in_front_bbox:
            return {
                "object_name": obj.name,
                "visibility_verdict": "outside_frame",
                "projection_status": "behind_view",
                "projection": {
                    "projected_center": {
                        "x": float(projected_center["x"]),
                        "y": float(projected_center["y"]),
                    },
                    "center_offset": {
                        "x": float(projected_center["x"]) - 0.5,
                        "y": float(projected_center["y"]) - 0.5,
                    },
                    "frame_coverage_ratio": 0.0,
                    "frame_occupancy_ratio": 0.0,
                    "centered": False,
                    "sample_count": len(visibility_points),
                    "in_front_sample_count": 0,
                    "in_frame_sample_count": 0,
                    "visible_sample_count": 0,
                    "occluded_sample_count": 0,
                    "occlusion_test_available": False,
                },
            }

        min_x = min(float(item["x"]) for item in in_front_bbox)
        max_x = max(float(item["x"]) for item in in_front_bbox)
        min_y = min(float(item["y"]) for item in in_front_bbox)
        max_y = max(float(item["y"]) for item in in_front_bbox)
        raw_width = max(0.0, max_x - min_x)
        raw_height = max(0.0, max_y - min_y)
        clamped_min_x = self._clamp_unit(min_x)
        clamped_max_x = self._clamp_unit(max_x)
        clamped_min_y = self._clamp_unit(min_y)
        clamped_max_y = self._clamp_unit(max_y)
        clamped_width = max(0.0, clamped_max_x - clamped_min_x)
        clamped_height = max(0.0, clamped_max_y - clamped_min_y)
        raw_area = raw_width * raw_height
        clamped_area = clamped_width * clamped_height
        frame_coverage_ratio = (clamped_area / raw_area) if raw_area > 1e-6 else (1.0 if clamped_area > 0.0 else 0.0)
        frame_occupancy_ratio = clamped_area

        projected_visibility_points = [
            (point, self._project_point_to_camera(scene, camera_obj, point)) for point in visibility_points
        ]
        visibility_samples = [(point, proj) for point, proj in projected_visibility_points if proj is not None]
        in_front_visibility = [(point, proj) for point, proj in visibility_samples if float(proj["z"]) >= 0.0]
        in_frame_visibility = [
            (point, proj)
            for point, proj in in_front_visibility
            if 0.0 <= float(proj["x"]) <= 1.0 and 0.0 <= float(proj["y"]) <= 1.0
        ]

        visible_sample_count = 0
        occluded_sample_count = 0
        occlusion_results = []
        for point, _proj in in_frame_visibility:
            is_visible = self._target_visible_from_camera(scene, camera_obj, obj, point)
            if is_visible is None:
                continue
            occlusion_results.append(is_visible)
            if is_visible:
                visible_sample_count += 1
            else:
                occluded_sample_count += 1

        occlusion_test_available = bool(occlusion_results)
        center_offset_x = float(projected_center["x"]) - 0.5
        center_offset_y = float(projected_center["y"]) - 0.5
        centered = math.hypot(center_offset_x, center_offset_y) <= 0.18

        if not in_frame_visibility or frame_coverage_ratio <= 0.0:
            visibility_verdict = "outside_frame"
            projection_status = "outside_frame"
        elif occlusion_test_available and visible_sample_count == 0 and occluded_sample_count > 0:
            visibility_verdict = "fully_occluded"
            projection_status = "projected"
        elif (
            frame_coverage_ratio < 0.999
            or (occlusion_test_available and occluded_sample_count > 0)
            or len(in_frame_visibility) < len(in_front_visibility)
        ):
            visibility_verdict = "partially_visible"
            projection_status = "projected"
        else:
            visibility_verdict = "visible"
            projection_status = "projected"

        return {
            "object_name": obj.name,
            "visibility_verdict": visibility_verdict,
            "projection_status": projection_status,
            "projection": {
                "projected_center": {
                    "x": float(projected_center["x"]),
                    "y": float(projected_center["y"]),
                },
                "projected_extent": {
                    "min_x": min_x,
                    "min_y": min_y,
                    "max_x": max_x,
                    "max_y": max_y,
                    "width": raw_width,
                    "height": raw_height,
                },
                "center_offset": {
                    "x": center_offset_x,
                    "y": center_offset_y,
                },
                "frame_coverage_ratio": frame_coverage_ratio,
                "frame_occupancy_ratio": frame_occupancy_ratio,
                "centered": centered,
                "sample_count": len(visibility_points),
                "in_front_sample_count": len(in_front_visibility),
                "in_frame_sample_count": len(in_frame_visibility),
                "visible_sample_count": visible_sample_count,
                "occluded_sample_count": occluded_sample_count,
                "occlusion_test_available": occlusion_test_available,
            },
        }

    def _summarize_view_diagnostics(self, target_diagnostics):
        summary = {
            "target_count": len(target_diagnostics),
            "visible_count": 0,
            "partially_visible_count": 0,
            "fully_occluded_count": 0,
            "outside_frame_count": 0,
            "unavailable_count": 0,
            "centered_target_count": 0,
            "framing_issue_count": 0,
        }

        for item in target_diagnostics:
            verdict = str(item.get("visibility_verdict") or "unavailable")
            projection = item.get("projection") or {}
            centered = bool(projection.get("centered")) if isinstance(projection, dict) else False
            coverage_ratio = (
                float(projection.get("frame_coverage_ratio"))
                if isinstance(projection, dict) and projection.get("frame_coverage_ratio") is not None
                else None
            )

            if verdict == "visible":
                summary["visible_count"] += 1
            elif verdict == "partially_visible":
                summary["partially_visible_count"] += 1
            elif verdict == "fully_occluded":
                summary["fully_occluded_count"] += 1
            elif verdict == "outside_frame":
                summary["outside_frame_count"] += 1
            else:
                summary["unavailable_count"] += 1

            if centered:
                summary["centered_target_count"] += 1
            if verdict in {"partially_visible", "fully_occluded", "outside_frame"} or (
                coverage_ratio is not None and coverage_ratio < 0.999
            ):
                summary["framing_issue_count"] += 1

        return summary

    def _mirror_user_view_to_temp_camera(self, scene, view_area, view_region, view_space):
        original_camera = scene.camera
        temp_camera_obj = None
        try:
            bpy.ops.object.camera_add()
            temp_camera_obj = bpy.context.active_object
            region_3d = getattr(view_space, "region_3d", None)
            if (
                temp_camera_obj is not None
                and getattr(temp_camera_obj, "data", None) is not None
                and str(getattr(region_3d, "view_perspective", "") or "").upper() == "ORTHO"
            ):
                temp_camera_obj.data.type = "ORTHO"
            scene.camera = temp_camera_obj
            with bpy.context.temp_override(area=view_area, region=view_region):
                bpy.ops.view3d.camera_to_view()
            return temp_camera_obj
        except Exception:
            if temp_camera_obj is not None:
                try:
                    scene.camera = original_camera
                except Exception:
                    pass
                try:
                    bpy.data.objects.remove(temp_camera_obj, do_unlink=True)
                except Exception:
                    pass
            raise

    def get_view_diagnostics(
        self,
        target_object=None,
        target_objects=None,
        camera_name=None,
        focus_target=None,
        view_name=None,
        orbit_horizontal=0.0,
        orbit_vertical=0.0,
        zoom_factor=None,
        persist_view=False,
    ):
        """Returns compact machine-readable view-space diagnostics for selected objects."""
        scene = bpy.context.scene
        target_names = self._resolve_view_target_names(target_object=target_object, target_objects=target_objects)
        if not target_names:
            raise ValueError("Provide target_object or target_objects for scene view diagnostics.")

        original_mode = None
        original_camera = scene.camera
        original_active = bpy.context.view_layer.objects.active
        original_selected = [obj for obj in bpy.context.view_layer.objects if obj.select_get()]
        view_area, view_region, view_space, _rv3d = self._find_view3d_context()
        original_view_state = None
        temp_camera_obj = None
        user_view_state_mutated = False
        state_restored = True
        result = None

        if bpy.context.active_object:
            original_mode = bpy.context.active_object.mode
            if original_mode != "OBJECT":
                try:
                    bpy.ops.object.mode_set(mode="OBJECT")
                except Exception:
                    pass

        if view_space:
            try:
                original_view_state = self.get_view_state()
            except Exception:
                original_view_state = None

        requested_view_source = (
            "named_camera" if camera_name and camera_name != "USER_PERSPECTIVE" else "user_perspective"
        )
        analysis_backend = "scene_camera" if requested_view_source == "named_camera" else "mirrored_user_perspective"

        try:
            use_explicit_scene_camera = requested_view_source == "named_camera"
            view_name_value = str(view_name).upper() if view_name is not None else None
            zoom_value = float(zoom_factor) if zoom_factor is not None else None
            orbit_h = float(orbit_horizontal or 0.0)
            orbit_v = float(orbit_vertical or 0.0)
            has_user_view_adjustment = bool(view_name_value or orbit_h or orbit_v or zoom_value is not None)
            analysis_camera = None

            if use_explicit_scene_camera:
                if has_user_view_adjustment:
                    raise ValueError(
                        "view_name/orbit/zoom options are only supported with USER_PERSPECTIVE diagnostics."
                    )
                analysis_camera = bpy.data.objects.get(camera_name)
                if analysis_camera is None:
                    raise ValueError(f"Camera '{camera_name}' not found.")
                if getattr(analysis_camera, "type", None) != "CAMERA":
                    raise ValueError(f"Object '{camera_name}' is not a camera.")
            else:
                if not view_area or not view_region or not view_space:
                    result = {
                        "view_query": {
                            "requested_view_source": requested_view_source,
                            "resolved_view_source": None,
                            "requested_camera_name": None,
                            "resolved_camera_name": None,
                            "analysis_backend": analysis_backend,
                            "available": False,
                            "unavailable_reason": "active_user_viewport_required",
                            "state_restored": True,
                        },
                        "targets": [
                            {
                                "object_name": name,
                                "visibility_verdict": "unavailable",
                                "projection_status": "unavailable",
                                "unavailable_reason": "active_user_viewport_required",
                            }
                            for name in target_names
                        ],
                        "summary": self._summarize_view_diagnostics(
                            [
                                {
                                    "object_name": name,
                                    "visibility_verdict": "unavailable",
                                    "projection_status": "unavailable",
                                }
                                for name in target_names
                            ]
                        ),
                    }
                    return result

                if view_name_value:
                    self.set_standard_view(view_name_value)
                    user_view_state_mutated = True

                if focus_target:
                    self.camera_focus(focus_target, zoom_factor=zoom_value or 1.0)
                    user_view_state_mutated = True
                elif zoom_value is not None:
                    if zoom_value <= 0:
                        raise ValueError("zoom_factor must be > 0")
                    rv3d = getattr(view_space, "region_3d", None)
                    if rv3d is not None:
                        rv3d.view_distance = float(rv3d.view_distance) / zoom_value
                        user_view_state_mutated = True

                if orbit_h or orbit_v:
                    self.camera_orbit(
                        angle_horizontal=orbit_h,
                        angle_vertical=orbit_v,
                        target_object=focus_target,
                    )
                    user_view_state_mutated = True

                temp_camera_obj = self._mirror_user_view_to_temp_camera(scene, view_area, view_region, view_space)
                analysis_camera = temp_camera_obj

            target_diagnostics = []
            for name in target_names:
                obj = bpy.data.objects.get(name)
                if obj is None:
                    target_diagnostics.append(
                        {
                            "object_name": name,
                            "visibility_verdict": "unavailable",
                            "projection_status": "unavailable",
                            "unavailable_reason": "object_not_found",
                        }
                    )
                    continue
                target_diagnostics.append(self._build_view_target_diagnostic(scene, analysis_camera, obj))

            result = {
                "view_query": {
                    "requested_view_source": requested_view_source,
                    "resolved_view_source": requested_view_source,
                    "requested_camera_name": camera_name if use_explicit_scene_camera else None,
                    "resolved_camera_name": getattr(analysis_camera, "name", None)
                    if use_explicit_scene_camera
                    else None,
                    "analysis_backend": analysis_backend,
                    "available": True,
                    "unavailable_reason": None,
                    "state_restored": True,
                },
                "targets": target_diagnostics,
                "summary": self._summarize_view_diagnostics(target_diagnostics),
            }
            return result
        finally:
            if temp_camera_obj is not None:
                scene.camera = original_camera

            if (
                original_view_state
                and requested_view_source == "user_perspective"
                and not persist_view
                and (user_view_state_mutated or temp_camera_obj is not None)
            ):
                try:
                    self.restore_view_state(original_view_state)
                except Exception:
                    state_restored = False

            bpy.ops.object.select_all(action="DESELECT")
            for obj in original_selected:
                try:
                    obj.select_set(True)
                except Exception:
                    continue

            if original_active and original_active.name in bpy.data.objects:
                bpy.context.view_layer.objects.active = original_active

            if temp_camera_obj is not None:
                try:
                    bpy.data.objects.remove(temp_camera_obj, do_unlink=True)
                except Exception:
                    state_restored = False

            if original_mode and original_mode != "OBJECT":
                if bpy.context.active_object:
                    try:
                        bpy.ops.object.mode_set(mode=original_mode)
                    except Exception:
                        state_restored = False

            if result is not None:
                result["view_query"]["state_restored"] = state_restored

    def get_view_state(self):
        """Returns a best-effort snapshot of the active 3D viewport state."""
        rv3d = None

        for area in bpy.context.screen.areas:
            if area.type == "VIEW_3D":
                for space in area.spaces:
                    if space.type == "VIEW_3D":
                        rv3d = space.region_3d
                        break
                break

        if not rv3d:
            return {"available": False}

        rotation = getattr(rv3d, "view_rotation", None)
        try:
            rotation_values = [float(rotation.w), float(rotation.x), float(rotation.y), float(rotation.z)]
        except Exception:
            try:
                rotation_values = [float(value) for value in rotation]
            except Exception:
                rotation_values = None

        try:
            view_location = [float(value) for value in rv3d.view_location]
        except Exception:
            view_location = None

        try:
            view_distance = float(rv3d.view_distance)
        except Exception:
            view_distance = None

        view_perspective = getattr(rv3d, "view_perspective", None)

        return {
            "available": True,
            "view_location": view_location,
            "view_distance": view_distance,
            "view_rotation": rotation_values,
            "view_perspective": view_perspective,
        }

    def restore_view_state(self, view_state):
        """Restores a previously captured 3D viewport state."""
        from mathutils import Quaternion, Vector

        rv3d = None

        for area in bpy.context.screen.areas:
            if area.type == "VIEW_3D":
                for space in area.spaces:
                    if space.type == "VIEW_3D":
                        rv3d = space.region_3d
                        break
                break

        if not rv3d:
            return "No 3D viewport found. View-state restore requires an active 3D view."

        if not isinstance(view_state, dict):
            raise ValueError("view_state must be an object/dict")

        if view_state.get("view_location") is not None:
            rv3d.view_location = Vector(view_state["view_location"])
        if view_state.get("view_distance") is not None:
            rv3d.view_distance = float(view_state["view_distance"])
        if view_state.get("view_rotation") is not None:
            rv3d.view_rotation = Quaternion(view_state["view_rotation"])
        if view_state.get("view_perspective") is not None:
            rv3d.view_perspective = str(view_state["view_perspective"])

        return "Restored 3D viewport state"

    def set_standard_view(self, view_name):
        """Sets the active 3D viewport to a standard orientation."""
        resolved = str(view_name).upper()
        if resolved not in {"FRONT", "RIGHT", "TOP"}:
            raise ValueError("view_name must be one of FRONT, RIGHT, TOP")

        view_area = None
        view_region = None

        for area in bpy.context.screen.areas:
            if area.type == "VIEW_3D":
                view_area = area
                for region in area.regions:
                    if region.type == "WINDOW":
                        view_region = region
                        break
                break

        if not view_area or not view_region:
            return "No 3D viewport found. Standard view requires an active 3D view."

        with bpy.context.temp_override(area=view_area, region=view_region):
            bpy.ops.view3d.view_axis(type=resolved)

        return f"Set 3D viewport to {resolved} view"
