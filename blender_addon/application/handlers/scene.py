import base64
import math
import os
import tempfile
from typing import Callable

import bpy

from .job_utils import raise_if_cancelled


class SceneHandler:
    """Application service for scene operations."""

    def list_objects(self):
        """Returns a list of objects in the scene."""
        objects = []
        for obj in bpy.context.scene.objects:
            objects.append({"name": obj.name, "type": obj.type, "location": [round(c, 3) for c in obj.location]})
        return objects

    def delete_object(self, name):
        """Deletes an object by name."""
        if name not in bpy.data.objects:
            raise ValueError(f"Object '{name}' not found")

        obj = bpy.data.objects[name]
        bpy.data.objects.remove(obj, do_unlink=True)
        return {"deleted": name}

    def clean_scene(self, keep_lights_and_cameras=True):
        """
        Deletes objects from the scene.
        If keep_lights_and_cameras is True, preserves LIGHT and CAMERA objects.
        """
        # Ensure we're in OBJECT mode before deleting
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        # Select all objects
        bpy.ops.object.select_all(action="DESELECT")

        to_delete = []
        for obj in bpy.context.scene.objects:
            if keep_lights_and_cameras:
                # Delete only geometry/helper types
                if obj.type in [
                    "MESH",
                    "CURVE",
                    "SURFACE",
                    "META",
                    "FONT",
                    "HAIR",
                    "POINTCLOUD",
                    "VOLUME",
                    "EMPTY",
                    "LATTICE",
                    "ARMATURE",
                ]:
                    to_delete.append(obj)
            else:
                # Delete everything
                to_delete.append(obj)

        for obj in to_delete:
            bpy.data.objects.remove(obj, do_unlink=True)

        # If hard reset, also clear collections (optional but good for full reset)
        if not keep_lights_and_cameras:
            for col in bpy.data.collections:
                if col.users == 0:  # Remove orphans
                    bpy.data.collections.remove(col)

        return {"count": len(to_delete), "kept_environment": keep_lights_and_cameras}

    def duplicate_object(self, name, translation=None):
        """Duplicates an object and optionally translates it."""
        if name not in bpy.data.objects:
            raise ValueError(f"Object '{name}' not found")

        obj = bpy.data.objects[name]

        # Ensure we're in OBJECT mode
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        # Deselect all, select target
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        # Duplicate
        bpy.ops.object.duplicate()
        new_obj = bpy.context.view_layer.objects.active

        # Translate if needed
        if translation:
            bpy.ops.transform.translate(value=translation)

        return {"original": name, "new_object": new_obj.name, "location": [round(c, 3) for c in new_obj.location]}

    def set_active_object(self, name):
        """Sets the active object."""
        if name not in bpy.data.objects:
            raise ValueError(f"Object '{name}' not found")

        # Ensure we're in OBJECT mode
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        obj = bpy.data.objects[name]
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        return {"active": name}

    def get_mode(self):
        """Reports the current Blender interaction mode and selection summary."""
        mode = getattr(bpy.context, "mode", "UNKNOWN")
        active_obj = getattr(bpy.context, "active_object", None)
        active_name = active_obj.name if active_obj else None
        active_type = getattr(active_obj, "type", None) if active_obj else None

        selected_names = []
        try:
            selected = getattr(bpy.context, "selected_objects", [])
            if selected:
                selected_names = [obj.name for obj in selected if hasattr(obj, "name")]
        except Exception:
            selected_names = []

        return {
            "mode": mode,
            "active_object": active_name,
            "active_object_type": active_type,
            "selected_object_names": selected_names,
            "selection_count": len(selected_names),
        }

    def list_selection(self):
        """Summarizes current selection for Object and Edit modes."""
        mode = getattr(bpy.context, "mode", "UNKNOWN")
        selected = getattr(bpy.context, "selected_objects", []) or []
        selected_names = [obj.name for obj in selected if hasattr(obj, "name")]

        summary = {
            "mode": mode,
            "selected_object_names": selected_names,
            "selection_count": len(selected_names),
            "edit_mode_vertex_count": None,
            "edit_mode_edge_count": None,
            "edit_mode_face_count": None,
        }

        if mode.startswith("EDIT"):
            obj = getattr(bpy.context, "edit_object", None) or getattr(bpy.context, "active_object", None)
            if obj and obj.type == "MESH":
                try:
                    import bmesh

                    bm = bmesh.from_edit_mesh(obj.data)
                    summary["edit_mode_vertex_count"] = sum(1 for v in bm.verts if v.select)
                    summary["edit_mode_edge_count"] = sum(1 for e in bm.edges if e.select)
                    summary["edit_mode_face_count"] = sum(1 for f in bm.faces if f.select)
                except Exception:
                    # If bmesh access fails, leave counts as None
                    pass

        return summary

    def inspect_object(self, name):
        """Returns a structured report containing object metadata."""
        obj = bpy.data.objects.get(name)
        if obj is None:
            raise ValueError(f"Object '{name}' not found")

        data = {
            "object_name": obj.name,
            "type": obj.type,
            "location": self._vec_to_list(getattr(obj, "location", (0.0, 0.0, 0.0))),
            "rotation": self._vec_to_list(getattr(obj, "rotation_euler", (0.0, 0.0, 0.0))),
            "scale": self._vec_to_list(getattr(obj, "scale", (1.0, 1.0, 1.0))),
            "dimensions": self._vec_to_list(getattr(obj, "dimensions", (0.0, 0.0, 0.0))),
            "collections": [col.name for col in getattr(obj, "users_collection", [])],
            "material_slots": self._gather_material_slots(obj),
            "modifiers": self._gather_modifiers(obj),
            "custom_properties": self._gather_custom_properties(obj),
        }

        mesh_stats = self._gather_mesh_stats(obj)
        if mesh_stats:
            data["mesh_stats"] = mesh_stats

        return data

    def _vec_to_list(self, value):
        try:
            return [round(float(v), 4) for v in value]
        except Exception:
            return [float(value) if isinstance(value, (int, float)) else 0.0]

    def _gather_material_slots(self, obj):
        slots = []
        for index, slot in enumerate(getattr(obj, "material_slots", []) or []):
            material = getattr(slot, "material", None)
            slots.append(
                {
                    "slot_index": index,
                    "slot_name": getattr(slot, "name", None),
                    "material_name": material.name if material else None,
                }
            )
        return slots

    def _gather_modifiers(self, obj):
        mods = []
        for mod in getattr(obj, "modifiers", []) or []:
            mods.append(
                {
                    "name": getattr(mod, "name", None),
                    "type": getattr(mod, "type", None),
                    "show_viewport": getattr(mod, "show_viewport", True),
                    "show_render": getattr(mod, "show_render", True),
                }
            )
        return mods

    def _gather_custom_properties(self, obj):
        custom = {}
        try:
            for key in obj.keys():
                if key.startswith("_"):
                    continue
                value = obj.get(key)
                if isinstance(value, (int, float, str, bool)):
                    custom[key] = value
                else:
                    custom[key] = str(value)
        except Exception:
            return {}
        return custom

    def _gather_mesh_stats(self, obj):
        if obj.type != "MESH":
            return None

        mesh = None
        try:
            depsgraph = bpy.context.evaluated_depsgraph_get()
        except Exception:
            depsgraph = None

        obj_eval = obj
        if depsgraph is not None:
            try:
                obj_eval = obj.evaluated_get(depsgraph)
            except Exception:
                obj_eval = obj

        try:
            mesh = obj_eval.to_mesh()
        except Exception:
            mesh = getattr(obj_eval, "data", None)

        if mesh is None:
            return None

        stats = {
            "vertices": len(getattr(mesh, "vertices", [])),
            "edges": len(getattr(mesh, "edges", [])),
            "faces": len(getattr(mesh, "polygons", [])),
        }
        try:
            mesh.calc_loop_triangles()
            stats["triangles"] = len(getattr(mesh, "loop_triangles", []))
        except Exception:
            stats["triangles"] = None

        if hasattr(obj_eval, "to_mesh_clear"):
            try:
                obj_eval.to_mesh_clear()
            except Exception:
                pass

        return stats

    def get_viewport(
        self,
        width=1024,
        height=768,
        shading="SOLID",
        camera_name=None,
        focus_target=None,
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

            if view_space:
                original_shading_type = view_space.shading.type

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

            try:
                # Case A: Specific existing camera
                if use_explicit_scene_camera:
                    if camera_name in bpy.data.objects:
                        scene.camera = bpy.data.objects[camera_name]
                    else:
                        raise ValueError(f"Camera '{camera_name}' not found.")

                # Case B: Dynamic View (User Perspective)
                else:
                    # Create temp camera
                    bpy.ops.object.camera_add()
                    temp_camera_obj = bpy.context.active_object
                    scene.camera = temp_camera_obj

                    # Deselect all first
                    bpy.ops.object.select_all(action="DESELECT")

                    # Select target(s) for framing
                    if focus_target:
                        if focus_target in bpy.data.objects:
                            target_obj = bpy.data.objects[focus_target]
                            target_obj.select_set(True)
                        else:
                            bpy.ops.object.select_all(action="SELECT")
                    else:
                        # No target -> Select all visible objects
                        bpy.ops.object.select_all(action="SELECT")

                    # Frame the camera to selection
                    if view_area and view_region:
                        with bpy.context.temp_override(area=view_area, region=view_region):
                            bpy.ops.view3d.camera_to_view_selected()
                    else:
                        # Fallback positioning without 3D view context
                        temp_camera_obj.location = (10, -10, 10)
                        # Approximate look at center
                        temp_camera_obj.rotation_euler = (math.radians(60), 0, math.radians(45))

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

    def create_light(self, type="POINT", energy=1000.0, color=(1.0, 1.0, 1.0), location=(0.0, 0.0, 0.0), name=None):
        """Creates a light source."""
        # Create light data
        light_data = bpy.data.lights.new(name=name if name else "Light", type=type)
        light_data.energy = energy
        light_data.color = color

        # Create object
        light_obj = bpy.data.objects.new(name=name if name else "Light", object_data=light_data)
        light_obj.location = location

        # Link to collection
        bpy.context.collection.objects.link(light_obj)

        return light_obj.name

    def create_camera(
        self,
        location=(0.0, -10.0, 0.0),
        rotation=(1.57, 0.0, 0.0),
        lens=50.0,
        clip_start=0.1,
        clip_end=100.0,
        name=None,
    ):
        """Creates a camera."""
        # Create camera data
        cam_data = bpy.data.cameras.new(name=name if name else "Camera")
        cam_data.lens = lens
        if clip_start is not None:
            cam_data.clip_start = clip_start
        if clip_end is not None:
            cam_data.clip_end = clip_end

        # Create object
        cam_obj = bpy.data.objects.new(name=name if name else "Camera", object_data=cam_data)
        cam_obj.location = location
        cam_obj.rotation_euler = rotation

        # Link to collection
        bpy.context.collection.objects.link(cam_obj)

        return cam_obj.name

    def create_empty(self, type="PLAIN_AXES", size=1.0, location=(0.0, 0.0, 0.0), name=None):
        """Creates an empty object."""
        empty_obj = bpy.data.objects.new(name if name else "Empty", None)
        empty_obj.empty_display_type = type
        empty_obj.empty_display_size = size
        empty_obj.location = location

        # Link to collection
        bpy.context.collection.objects.link(empty_obj)

        return empty_obj.name

    def set_mode(self, mode="OBJECT"):
        """Switch Blender context mode."""
        mode = mode.upper()
        valid_modes = ["OBJECT", "EDIT", "SCULPT", "VERTEX_PAINT", "WEIGHT_PAINT", "TEXTURE_PAINT", "POSE"]

        if mode not in valid_modes:
            raise ValueError(f"Invalid mode '{mode}'. Valid: {valid_modes}")

        current_mode = bpy.context.mode

        if current_mode == mode or current_mode.startswith(mode):
            return f"Already in {mode} mode"

        active_obj = bpy.context.active_object

        if mode != "OBJECT" and not active_obj:
            raise ValueError(f"Cannot enter {mode} mode: no active object")

        # Validate object type for specific modes
        if mode == "EDIT":
            valid_types = ["MESH", "CURVE", "SURFACE", "META", "FONT", "LATTICE", "ARMATURE"]
            if active_obj.type not in valid_types:
                raise ValueError(
                    f"Cannot enter {mode} mode: active object '{active_obj.name}' "
                    f"is type '{active_obj.type}'. Supported types: {', '.join(valid_types)}"
                )
        elif mode == "SCULPT":
            if active_obj.type != "MESH":
                raise ValueError(
                    f"Cannot enter SCULPT mode: active object '{active_obj.name}' is type '{active_obj.type}'. Only MESH supported."
                )
        elif mode == "POSE":
            if active_obj.type != "ARMATURE":
                raise ValueError(
                    f"Cannot enter POSE mode: active object '{active_obj.name}' is type '{active_obj.type}'. Only ARMATURE supported."
                )

        bpy.ops.object.mode_set(mode=mode)
        return f"Switched to {mode} mode"

    def snapshot_state(self, include_mesh_stats=False, include_materials=False):
        """Captures a lightweight JSON snapshot of the scene state."""
        import hashlib
        import json
        from datetime import datetime, timezone

        # Collect object data in deterministic order (alphabetical by name)
        objects_data = []
        for obj in sorted(bpy.context.scene.objects, key=lambda o: o.name):
            obj_data = {
                "name": obj.name,
                "type": obj.type,
                "location": self._vec_to_list(obj.location),
                "rotation": self._vec_to_list(obj.rotation_euler),
                "scale": self._vec_to_list(obj.scale),
                "parent": obj.parent.name if obj.parent else None,
                "visible": not bool(getattr(obj, "hide_viewport", False)),
                "selected": obj.select_get(),
                "collections": [col.name for col in obj.users_collection],
            }

            # Optional: Include modifiers info
            if obj.modifiers:
                obj_data["modifiers"] = [{"name": mod.name, "type": mod.type} for mod in obj.modifiers]

            # Optional: Include mesh stats
            if include_mesh_stats and obj.type == "MESH":
                mesh_stats = self._gather_mesh_stats(obj)
                if mesh_stats:
                    obj_data["mesh_stats"] = mesh_stats

            # Optional: Include material info
            if include_materials and obj.material_slots:
                obj_data["materials"] = [slot.material.name if slot.material else None for slot in obj.material_slots]

            objects_data.append(obj_data)

        # Build snapshot payload
        snapshot = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "object_count": len(objects_data),
            "objects": objects_data,
            "active_object": bpy.context.active_object.name if bpy.context.active_object else None,
            "mode": getattr(bpy.context, "mode", "UNKNOWN"),
        }

        # Compute hash for change detection (SHA256 of scene state, excluding timestamp)
        # This ensures identical scenes produce identical hashes
        state_for_hash = {
            "object_count": snapshot["object_count"],
            "objects": snapshot["objects"],
            "active_object": snapshot["active_object"],
            "mode": snapshot["mode"],
        }
        state_json = json.dumps(state_for_hash, sort_keys=True)
        snapshot_hash = hashlib.sha256(state_json.encode("utf-8")).hexdigest()

        # Return snapshot with hash
        return {"hash": snapshot_hash, "snapshot": snapshot}

    def inspect_mesh_topology(self, object_name, detailed=False):
        """Reports detailed topology stats for a given mesh."""
        if object_name not in bpy.data.objects:
            raise ValueError(f"Object '{object_name}' not found")

        obj = bpy.data.objects[object_name]
        if obj.type != "MESH":
            raise ValueError(f"Object '{object_name}' is not a MESH (type: {obj.type})")

        import bmesh

        # Create a new BMesh to inspect data safely without affecting the scene
        bm = bmesh.new()

        try:
            # Load mesh data
            # Note: If object is in Edit Mode, this gets the underlying mesh data
            # which might not include uncommitted bmesh changes.
            # For 100% accuracy in Edit Mode, we'd need bmesh.from_edit_mesh,
            # but that requires being in Edit Mode context.
            # For a general introspection tool, looking at obj.data is standard.
            bm.from_mesh(obj.data)

            bm.verts.ensure_lookup_table()
            bm.edges.ensure_lookup_table()
            bm.faces.ensure_lookup_table()

            stats = {
                "object_name": obj.name,
                "vertex_count": len(bm.verts),
                "edge_count": len(bm.edges),
                "face_count": len(bm.faces),
                "triangle_count": 0,
                "quad_count": 0,
                "ngon_count": 0,
                # Default these to 0/None unless detailed check runs
                "non_manifold_edges": 0 if detailed else None,
                "loose_vertices": 0 if detailed else None,
                "loose_edges": 0 if detailed else None,
            }

            # Face type counts
            for f in bm.faces:
                v_count = len(f.verts)
                if v_count == 3:
                    stats["triangle_count"] += 1
                elif v_count == 4:
                    stats["quad_count"] += 1
                else:
                    stats["ngon_count"] += 1

            if detailed:
                # Non-manifold edges (wire edges or edges shared by >2 faces)
                # is_manifold property handles this check
                stats["non_manifold_edges"] = sum(1 for e in bm.edges if not e.is_manifold)

                # Loose geometry
                stats["loose_vertices"] = sum(1 for v in bm.verts if not v.link_edges)
                stats["loose_edges"] = sum(1 for e in bm.edges if not e.link_faces)

            return stats

        finally:
            bm.free()

    def inspect_material_slots(self, material_filter=None, include_empty_slots=True):
        """Audits material slot assignments across the entire scene."""
        slot_data = []
        warnings = []

        # Iterate all objects in deterministic order
        for obj in sorted(bpy.context.scene.objects, key=lambda o: o.name):
            # Only process objects that can have materials
            if not hasattr(obj, "material_slots") or len(obj.material_slots) == 0:
                continue

            for slot_idx, slot in enumerate(obj.material_slots):
                mat_name = slot.material.name if slot.material else None

                # Apply material filter if provided
                if material_filter and mat_name != material_filter:
                    continue

                # Skip empty slots if requested
                if not include_empty_slots and mat_name is None:
                    continue

                slot_info = {
                    "object_name": obj.name,
                    "object_type": obj.type,
                    "slot_index": slot_idx,
                    "slot_name": slot.name,
                    "material_name": mat_name,
                    "is_empty": mat_name is None,
                }

                # Add warnings for problematic slots
                slot_warnings = []
                if mat_name is None:
                    slot_warnings.append("Empty slot (no material assigned)")
                elif mat_name not in bpy.data.materials:
                    slot_warnings.append(f"Material '{mat_name}' not found in bpy.data.materials")

                if slot_warnings:
                    slot_info["warnings"] = slot_warnings
                    warnings.extend([f"{obj.name}[{slot_idx}]: {w}" for w in slot_warnings])

                slot_data.append(slot_info)

        # Build summary
        empty_count = sum(1 for s in slot_data if s["is_empty"])
        assigned_count = len(slot_data) - empty_count

        return {
            "total_slots": len(slot_data),
            "assigned_slots": assigned_count,
            "empty_slots": empty_count,
            "warnings": warnings,
            "slots": slot_data,
        }

    def inspect_modifiers(self, object_name=None, include_disabled=True):
        """Audits modifier stacks for a specific object or the entire scene."""
        result = {"object_count": 0, "modifier_count": 0, "objects": []}

        objects_to_check = []
        if object_name:
            if object_name not in bpy.data.objects:
                raise ValueError(f"Object '{object_name}' not found")
            objects_to_check.append(bpy.data.objects[object_name])
        else:
            # Deterministic order
            objects_to_check = sorted(bpy.context.scene.objects, key=lambda o: o.name)

        for obj in objects_to_check:
            # Skip objects that don't support modifiers (e.g. Empty, Light)
            if not hasattr(obj, "modifiers") or len(obj.modifiers) == 0:
                continue

            modifiers = []
            for mod in obj.modifiers:
                # Check visibility (viewport or render)
                is_enabled = mod.show_viewport or mod.show_render
                if not include_disabled and not is_enabled:
                    continue

                mod_info = {
                    "name": mod.name,
                    "type": mod.type,
                    "is_enabled": is_enabled,
                    "show_viewport": mod.show_viewport,
                    "show_render": mod.show_render,
                }

                # Extract key properties based on type
                if mod.type == "SUBSURF":
                    mod_info["levels"] = mod.levels
                    mod_info["render_levels"] = mod.render_levels
                elif mod.type == "BEVEL":
                    mod_info["width"] = mod.width
                    mod_info["segments"] = mod.segments
                    mod_info["limit_method"] = mod.limit_method
                elif mod.type == "MIRROR":
                    mod_info["use_axis"] = [mod.use_axis[0], mod.use_axis[1], mod.use_axis[2]]
                    mod_info["mirror_object"] = mod.mirror_object.name if mod.mirror_object else None
                elif mod.type == "BOOLEAN":
                    mod_info["operation"] = mod.operation
                    mod_info["object"] = mod.object.name if mod.object else None
                    mod_info["solver"] = mod.solver
                elif mod.type == "ARRAY":
                    mod_info["count"] = mod.count
                    mod_info["use_relative_offset"] = mod.use_relative_offset
                    mod_info["use_constant_offset"] = mod.use_constant_offset
                elif mod.type == "SOLIDIFY":
                    mod_info["thickness"] = mod.thickness
                    mod_info["offset"] = mod.offset

                modifiers.append(mod_info)

            if modifiers:
                result["objects"].append({"name": obj.name, "modifiers": modifiers})
                result["modifier_count"] += len(modifiers)
                result["object_count"] += 1

        return result

    def inspect_render_settings(self):
        """Returns structured render settings for the active scene."""
        scene = bpy.context.scene
        render = scene.render
        image_settings = getattr(render, "image_settings", None)
        cycles = getattr(scene, "cycles", None)

        return {
            "render_engine": getattr(render, "engine", None),
            "resolution": {
                "x": getattr(render, "resolution_x", None),
                "y": getattr(render, "resolution_y", None),
                "percentage": getattr(render, "resolution_percentage", None),
            },
            "filepath": getattr(render, "filepath", None),
            "use_file_extension": getattr(render, "use_file_extension", None),
            "film_transparent": getattr(render, "film_transparent", None),
            "image_settings": {
                "file_format": getattr(image_settings, "file_format", None),
                "color_mode": getattr(image_settings, "color_mode", None),
                "color_depth": getattr(image_settings, "color_depth", None),
            },
            "cycles": {
                "device": getattr(cycles, "device", None),
                "samples": getattr(cycles, "samples", None),
                "preview_samples": getattr(cycles, "preview_samples", None),
            },
        }

    def inspect_color_management(self):
        """Returns structured color-management settings for the active scene."""
        scene = bpy.context.scene
        display_settings = getattr(scene, "display_settings", None)
        view_settings = getattr(scene, "view_settings", None)
        sequencer_settings = getattr(scene, "sequencer_colorspace_settings", None)

        return {
            "display_device": getattr(display_settings, "display_device", None),
            "view_transform": getattr(view_settings, "view_transform", None),
            "look": getattr(view_settings, "look", None),
            "exposure": getattr(view_settings, "exposure", None),
            "gamma": getattr(view_settings, "gamma", None),
            "use_curve_mapping": getattr(view_settings, "use_curve_mapping", None),
            "sequencer_color_space": getattr(sequencer_settings, "name", None),
        }

    def inspect_world(self):
        """Returns structured world/background settings for the active scene."""
        scene = bpy.context.scene
        world = getattr(scene, "world", None)
        if world is None:
            return {
                "world_name": None,
                "use_nodes": False,
                "color": None,
                "node_tree_name": None,
                "background": None,
                "node_graph_reference": None,
                "node_graph_handoff": self._build_world_node_graph_handoff(
                    world_name=None,
                    node_tree_name=None,
                    use_nodes=False,
                    background=None,
                ),
            }

        background = None
        if getattr(world, "use_nodes", False) and getattr(world, "node_tree", None) is not None:
            background = self._inspect_world_background_node(world.node_tree)

        node_tree_name = getattr(getattr(world, "node_tree", None), "name", None)
        world_name = getattr(world, "name", None)
        use_nodes = getattr(world, "use_nodes", False)

        return {
            "world_name": world_name,
            "use_nodes": use_nodes,
            "color": self._vec_to_list(getattr(world, "color", (0.0, 0.0, 0.0))),
            "node_tree_name": node_tree_name,
            "background": background,
            "node_graph_reference": self._build_world_node_graph_reference(
                world_name=world_name,
                node_tree_name=node_tree_name,
                background=background,
            ),
            "node_graph_handoff": self._build_world_node_graph_handoff(
                world_name=world_name,
                node_tree_name=node_tree_name,
                use_nodes=use_nodes,
                background=background,
            ),
        }

    def configure_render_settings(self, settings):
        """Applies grouped render settings and returns the resulting render snapshot."""
        settings = self._require_mapping(settings, "settings")
        scene = bpy.context.scene
        render = scene.render

        if "render_engine" in settings and settings["render_engine"] is not None:
            render.engine = self._require_string(settings["render_engine"], "render_engine")

        resolution = settings.get("resolution")
        if resolution is not None:
            resolution = self._require_mapping(resolution, "resolution")
            if "x" in resolution and resolution["x"] is not None:
                render.resolution_x = self._require_int(resolution["x"], "resolution.x")
            if "y" in resolution and resolution["y"] is not None:
                render.resolution_y = self._require_int(resolution["y"], "resolution.y")
            if "percentage" in resolution and resolution["percentage"] is not None:
                render.resolution_percentage = self._require_int(resolution["percentage"], "resolution.percentage")

        if "filepath" in settings and settings["filepath"] is not None:
            render.filepath = self._require_string(settings["filepath"], "filepath")
        if "use_file_extension" in settings and settings["use_file_extension"] is not None:
            render.use_file_extension = self._require_bool(settings["use_file_extension"], "use_file_extension")
        if "film_transparent" in settings and settings["film_transparent"] is not None:
            render.film_transparent = self._require_bool(settings["film_transparent"], "film_transparent")

        image_settings = settings.get("image_settings")
        if image_settings is not None:
            image_settings = self._require_mapping(image_settings, "image_settings")
            target = getattr(render, "image_settings", None)
            if target is None:
                raise ValueError("Render image_settings are not available on this scene.")
            if "file_format" in image_settings and image_settings["file_format"] is not None:
                target.file_format = self._require_string(image_settings["file_format"], "image_settings.file_format")
            if "color_mode" in image_settings and image_settings["color_mode"] is not None:
                target.color_mode = self._require_string(image_settings["color_mode"], "image_settings.color_mode")
            if "color_depth" in image_settings and image_settings["color_depth"] is not None:
                target.color_depth = self._require_string(image_settings["color_depth"], "image_settings.color_depth")

        cycles_settings = settings.get("cycles")
        if cycles_settings is not None:
            cycles_settings = self._require_mapping(cycles_settings, "cycles")
            cycles = getattr(scene, "cycles", None)
            if cycles is None:
                raise ValueError("Cycles settings are not available on this scene.")
            if "device" in cycles_settings and cycles_settings["device"] is not None:
                cycles.device = self._require_string(cycles_settings["device"], "cycles.device")
            if "samples" in cycles_settings and cycles_settings["samples"] is not None:
                cycles.samples = self._require_int(cycles_settings["samples"], "cycles.samples")
            if "preview_samples" in cycles_settings and cycles_settings["preview_samples"] is not None:
                cycles.preview_samples = self._require_int(cycles_settings["preview_samples"], "cycles.preview_samples")

        return self.inspect_render_settings()

    def configure_color_management(self, settings):
        """Applies grouped color-management settings and returns the resulting snapshot."""
        settings = self._require_mapping(settings, "settings")
        scene = bpy.context.scene
        display_settings = getattr(scene, "display_settings", None)
        view_settings = getattr(scene, "view_settings", None)
        sequencer_settings = getattr(scene, "sequencer_colorspace_settings", None)

        if "display_device" in settings and settings["display_device"] is not None:
            if display_settings is None:
                raise ValueError("display_settings are not available on this scene.")
            display_settings.display_device = self._require_string(settings["display_device"], "display_device")
        if "view_transform" in settings and settings["view_transform"] is not None:
            if view_settings is None:
                raise ValueError("view_settings are not available on this scene.")
            view_settings.view_transform = self._require_string(settings["view_transform"], "view_transform")
        if "look" in settings and settings["look"] is not None:
            if view_settings is None:
                raise ValueError("view_settings are not available on this scene.")
            view_settings.look = self._require_string(settings["look"], "look")
        if "exposure" in settings and settings["exposure"] is not None:
            if view_settings is None:
                raise ValueError("view_settings are not available on this scene.")
            view_settings.exposure = self._require_float(settings["exposure"], "exposure")
        if "gamma" in settings and settings["gamma"] is not None:
            if view_settings is None:
                raise ValueError("view_settings are not available on this scene.")
            view_settings.gamma = self._require_float(settings["gamma"], "gamma")
        if "use_curve_mapping" in settings and settings["use_curve_mapping"] is not None:
            if view_settings is None:
                raise ValueError("view_settings are not available on this scene.")
            view_settings.use_curve_mapping = self._require_bool(
                settings["use_curve_mapping"],
                "use_curve_mapping",
            )
        if "sequencer_color_space" in settings and settings["sequencer_color_space"] is not None:
            if sequencer_settings is None:
                raise ValueError("sequencer_colorspace_settings are not available on this scene.")
            sequencer_settings.name = self._require_string(
                settings["sequencer_color_space"],
                "sequencer_color_space",
            )

        return self.inspect_color_management()

    def configure_world(self, settings):
        """Applies grouped world/background settings and returns the resulting world snapshot."""
        settings = self._require_mapping(settings, "settings")
        scene = bpy.context.scene
        self._validate_world_settings_boundary(settings)

        if "world_name" in settings:
            world_name = settings["world_name"]
            if world_name is None:
                scene.world = None
            else:
                name = self._require_string(world_name, "world_name")
                world = getattr(bpy.data, "worlds", None)
                resolved_world = world.get(name) if world is not None else None
                if resolved_world is None:
                    raise ValueError(f"World '{name}' not found")
                scene.world = resolved_world

        world = getattr(scene, "world", None)
        remaining_keys = {key for key in settings if key != "world_name"}
        if world is None:
            if remaining_keys:
                raise ValueError("Scene has no world assigned. Provide 'world_name' before applying world settings.")
            return self.inspect_world()

        use_nodes_requested = None
        if "use_nodes" in settings and settings["use_nodes"] is not None:
            use_nodes_requested = self._require_bool(settings["use_nodes"], "use_nodes")
            world.use_nodes = use_nodes_requested

        if "color" in settings and settings["color"] is not None:
            world.color = self._require_color(settings["color"], "color", allow_alpha=False)

        background = settings.get("background")
        if background is not None:
            background = self._require_mapping(background, "background")
            unknown_background_keys = set(background) - {"color", "strength", "node_name"}
            if unknown_background_keys:
                keys = ", ".join(sorted(unknown_background_keys))
                raise ValueError(
                    f"Unsupported background fields: {keys}. Use future node_graph tooling for arbitrary world nodes."
                )
            if use_nodes_requested is False:
                raise ValueError("background settings require 'use_nodes' to be true.")
            if not getattr(world, "use_nodes", False):
                world.use_nodes = True
            background_node = self._ensure_world_background_node(world)
            if "color" in background and background["color"] is not None:
                color = self._require_color(background["color"], "background.color", allow_alpha=True)
                if len(color) == 3:
                    color = [color[0], color[1], color[2], 1.0]
                self._set_node_input_default(background_node, "Color", color)
            if "strength" in background and background["strength"] is not None:
                self._set_node_input_default(
                    background_node,
                    "Strength",
                    self._require_float(background["strength"], "background.strength"),
                )

        return self.inspect_world()

    def get_constraints(self, object_name, include_bones=False):
        """
        [OBJECT MODE][READ-ONLY][SAFE] Returns object (and optional bone) constraints.
        """
        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise ValueError(f"Object '{object_name}' not found")

        constraints = self._serialize_constraints(getattr(obj, "constraints", []))
        bone_constraints = []

        if include_bones and obj.type == "ARMATURE":
            pose = getattr(obj, "pose", None)
            if pose and hasattr(pose, "bones"):
                for bone in pose.bones:
                    bone_list = self._serialize_constraints(getattr(bone, "constraints", []))
                    if bone_list:
                        bone_constraints.append({"bone_name": bone.name, "constraints": bone_list})

        return {
            "object_name": object_name,
            "constraint_count": len(constraints),
            "constraints": constraints,
            "bone_constraints": bone_constraints,
        }

    def _serialize_constraints(self, constraints):
        return [self._serialize_constraint(constraint) for constraint in constraints]

    def _serialize_constraint(self, constraint):
        object_refs = []
        seen_refs = set()
        properties = {}

        for prop in sorted(constraint.bl_rna.properties, key=lambda p: p.identifier):
            if prop.identifier == "rna_type":
                continue
            try:
                value = getattr(constraint, prop.identifier)
            except Exception:
                continue

            properties[prop.identifier] = self._serialize_constraint_value(value, prop, object_refs, seen_refs)

        return {"name": constraint.name, "type": constraint.type, "properties": properties, "object_refs": object_refs}

    def _serialize_constraint_value(self, value, prop, object_refs, seen_refs):
        if prop.type == "POINTER":
            if value is None:
                return None
            if hasattr(value, "name"):
                key = (prop.identifier, value.name)
                if key not in seen_refs:
                    seen_refs.add(key)
                    object_refs.append({"property": prop.identifier, "object_name": value.name})
                return value.name
            return str(value)

        if prop.type == "COLLECTION":
            items = []
            try:
                for item in value:
                    items.append(self._serialize_constraint_collection_item(item))
            except Exception:
                return []
            return items

        return self._serialize_simple_value(value)

    def _serialize_constraint_collection_item(self, item):
        if hasattr(item, "target"):
            target = getattr(item, "target", None)
            entry = {"target": target.name if target else None}
            subtarget = getattr(item, "subtarget", None)
            if subtarget:
                entry["subtarget"] = subtarget
            if hasattr(item, "weight"):
                entry["weight"] = round(float(item.weight), 6)
            return entry

        if hasattr(item, "name"):
            return item.name

        return self._serialize_simple_value(item)

    def _serialize_simple_value(self, value):
        if isinstance(value, bool):
            return bool(value)
        if isinstance(value, int):
            return int(value)
        if isinstance(value, float):
            return round(float(value), 6)
        if isinstance(value, str):
            return value
        if isinstance(value, set):
            return sorted(value)
        if hasattr(value, "__iter__"):
            try:
                return [self._serialize_simple_value(v) for v in value]
            except Exception:
                pass
        if hasattr(value, "x") and hasattr(value, "y"):
            coords = [value.x, value.y]
            if hasattr(value, "z"):
                coords.append(value.z)
            if hasattr(value, "w"):
                coords.append(value.w)
            return [round(float(c), 6) for c in coords]
        if hasattr(value, "name"):
            return value.name
        return str(value)

    # TASK-043: Scene Utility Tools
    def rename_object(self, old_name, new_name):
        """Renames an object in the scene."""
        obj = bpy.data.objects.get(old_name)
        if obj is None:
            raise ValueError(f"Object '{old_name}' not found")

        obj.name = new_name
        # Note: Blender may add suffix if name already exists
        actual_name = obj.name

        if actual_name != new_name:
            return f"Renamed '{old_name}' to '{actual_name}' (suffix added due to name collision)"
        return f"Renamed '{old_name}' to '{actual_name}'"

    def hide_object(self, object_name, hide=True, hide_render=False):
        """Hides or shows an object in the viewport and/or render."""
        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise ValueError(f"Object '{object_name}' not found")

        obj.hide_viewport = hide
        if hide_render:
            obj.hide_render = hide

        state = "hidden" if hide else "visible"
        render_state = " (also in render)" if hide_render else ""
        return f"Object '{object_name}' is now {state}{render_state}"

    def show_all_objects(self, include_render=False):
        """Shows all hidden objects in the scene."""
        count = 0
        for obj in bpy.data.objects:
            if obj.hide_viewport:
                obj.hide_viewport = False
                count += 1
            if include_render and obj.hide_render:
                obj.hide_render = False

        render_note = " (including render visibility)" if include_render else ""
        return f"Made {count} objects visible{render_note}"

    def isolate_object(self, object_names):
        """Isolates object(s) by hiding all others."""
        # Validate all requested objects exist
        keep_visible = set(object_names)
        for name in keep_visible:
            if name not in bpy.data.objects:
                raise ValueError(f"Object '{name}' not found")

        hidden_count = 0
        for obj in bpy.data.objects:
            if obj.name not in keep_visible:
                if not obj.hide_viewport:
                    obj.hide_viewport = True
                    hidden_count += 1
            else:
                # Ensure isolated objects are visible
                obj.hide_viewport = False

        return f"Isolated {len(keep_visible)} object(s), hid {hidden_count} others"

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

    # TASK-045: Object Inspection Tools
    def get_custom_properties(self, object_name):
        """Gets custom properties (metadata) from an object."""
        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise ValueError(f"Object '{object_name}' not found")

        properties = {}
        try:
            for key in obj.keys():
                # Skip internal properties (start with underscore)
                if key.startswith("_"):
                    continue
                value = obj.get(key)
                # Convert to JSON-serializable types
                if isinstance(value, (int, float, str, bool)):
                    properties[key] = value
                elif hasattr(value, "__iter__") and not isinstance(value, str):
                    # Convert vectors/arrays to lists
                    try:
                        properties[key] = list(value)
                    except Exception:
                        properties[key] = str(value)
                else:
                    properties[key] = str(value)
        except Exception as e:
            raise ValueError(f"Failed to read custom properties: {e}")

        return {"object_name": object_name, "property_count": len(properties), "properties": properties}

    def set_custom_property(self, object_name, property_name, property_value, delete=False):
        """Sets or deletes a custom property on an object."""
        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise ValueError(f"Object '{object_name}' not found")

        if delete:
            if property_name in obj.keys():
                del obj[property_name]
                return f"Deleted property '{property_name}' from '{object_name}'"
            else:
                return f"Property '{property_name}' not found on '{object_name}'"

        # Set the property
        obj[property_name] = property_value
        return f"Set property '{property_name}' = {property_value} on '{object_name}'"

    def get_hierarchy(self, object_name=None, include_transforms=False):
        """Gets parent-child hierarchy for objects."""

        def build_hierarchy(obj, include_transforms):
            """Recursively builds hierarchy dict for an object."""
            node = {"name": obj.name, "type": obj.type, "children": []}

            if include_transforms:
                node["location"] = self._vec_to_list(obj.location)
                node["rotation"] = self._vec_to_list(obj.rotation_euler)
                node["scale"] = self._vec_to_list(obj.scale)

            # Find children
            for child in obj.children:
                node["children"].append(build_hierarchy(child, include_transforms))

            return node

        if object_name:
            # Get hierarchy for specific object
            obj = bpy.data.objects.get(object_name)
            if obj is None:
                raise ValueError(f"Object '{object_name}' not found")

            # Build hierarchy from this object down
            hierarchy = build_hierarchy(obj, include_transforms)

            # Also include parent chain
            parent_chain = []
            current = obj.parent
            while current:
                parent_chain.append(current.name)
                current = current.parent

            return {"root": hierarchy, "parent_chain": parent_chain}
        else:
            # Get all root objects (no parent)
            roots = []
            for obj in sorted(bpy.context.scene.objects, key=lambda o: o.name):
                if obj.parent is None:
                    roots.append(build_hierarchy(obj, include_transforms))

            return {"root_count": len(roots), "hierarchy": roots}

    def get_bounding_box(self, object_name, world_space=True):
        """Gets bounding box corners for an object."""
        obj = self._get_object_or_raise(object_name)
        bbox_data = self._get_bbox_data(obj, world_space=world_space)

        return {
            "object_name": object_name,
            "world_space": world_space,
            "min": self._round_values(bbox_data["min"], precision=4),
            "max": self._round_values(bbox_data["max"], precision=4),
            "center": self._round_values(bbox_data["center"], precision=4),
            "dimensions": self._round_values(bbox_data["dimensions"], precision=4),
            "corners": [self._round_values(corner, precision=4) for corner in bbox_data["corners"]],
        }

    def get_origin_info(self, object_name):
        """Gets origin (pivot point) information for an object."""
        import math

        obj = self._get_object_or_raise(object_name)
        origin = [float(obj.location[i]) for i in range(3)]
        bbox_data = self._get_bbox_data(obj, world_space=True)
        bbox_center = bbox_data["center"]
        offset_from_center = [origin[i] - bbox_center[i] for i in range(3)]

        # Determine origin type (approximate)
        origin_type = "CUSTOM"
        offset_magnitude = math.sqrt(sum(value * value for value in offset_from_center))

        if offset_magnitude < 0.001:
            origin_type = "CENTER"
        else:
            # Check if at bottom center
            min_z = bbox_data["min"][2]
            if (
                abs(origin[2] - min_z) < 0.001
                and abs(offset_from_center[0]) < 0.001
                and abs(offset_from_center[1]) < 0.001
            ):
                origin_type = "BOTTOM_CENTER"

        return {
            "object_name": object_name,
            "origin_world": self._round_values(origin, precision=4),
            "bbox_center": self._round_values(bbox_center, precision=4),
            "offset_from_center": self._round_values(offset_from_center, precision=4),
            "estimated_type": origin_type,
        }

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

        source_bbox = self._get_bbox_data(self._get_object_or_raise(from_object), world_space=True)
        target_bbox = self._get_bbox_data(self._get_object_or_raise(to_object), world_space=True)

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
            relation = "separated"
        elif all(value > tolerance for value in overlap_dimensions):
            relation = "overlapping"
        else:
            relation = "contact"

        return {
            "from_object": from_object,
            "to_object": to_object,
            "gap": round(float(gap_distance), 6),
            "axis_gap": self._round_axis_mapping(axis_gap),
            "relation": relation,
            "tolerance": round(float(tolerance), 6),
            "units": "blender_units",
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
        source_bbox = self._get_bbox_data(self._get_object_or_raise(from_object), world_space=True)
        target_bbox = self._get_bbox_data(self._get_object_or_raise(to_object), world_space=True)

        intersection_min = [
            max(source_bbox["min"][axis_index], target_bbox["min"][axis_index]) for axis_index in range(3)
        ]
        intersection_max = [
            min(source_bbox["max"][axis_index], target_bbox["max"][axis_index]) for axis_index in range(3)
        ]
        overlap_dimensions = [
            max(0.0, intersection_max[axis_index] - intersection_min[axis_index]) for axis_index in range(3)
        ]
        overlaps = all(value > tolerance for value in overlap_dimensions)
        gap_axes = [
            self._axis_gap(
                source_bbox["min"][axis_index],
                source_bbox["max"][axis_index],
                target_bbox["min"][axis_index],
                target_bbox["max"][axis_index],
            )
            for axis_index in range(3)
        ]
        touching = not overlaps and all(value <= tolerance for value in gap_axes)
        overlap_volume = 0.0
        if overlaps:
            overlap_volume = overlap_dimensions[0] * overlap_dimensions[1] * overlap_dimensions[2]

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
            "overlap_dimensions": self._round_values(overlap_dimensions),
            "overlap_volume": round(float(overlap_volume), 6),
            "intersection_min": self._round_values(intersection_min) if overlaps else None,
            "intersection_max": self._round_values(intersection_max) if overlaps else None,
            "tolerance": round(float(tolerance), 6),
            "units": "blender_units",
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

    def _get_object_or_raise(self, object_name):
        """Returns an object or raises a clear value error."""
        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise ValueError(f"Object '{object_name}' not found")
        return obj

    def _get_bbox_data(self, obj, world_space=True):
        """Returns raw bounding-box data for an object."""
        from mathutils import Vector

        corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box] if world_space else [
            Vector(corner) for corner in obj.bound_box
        ]
        min_corner = [float(min(corner[index] for corner in corners)) for index in range(3)]
        max_corner = [float(max(corner[index] for corner in corners)) for index in range(3)]
        center = [(min_corner[index] + max_corner[index]) / 2.0 for index in range(3)]
        dimensions = [max_corner[index] - min_corner[index] for index in range(3)]

        return {
            "min": min_corner,
            "max": max_corner,
            "center": center,
            "dimensions": dimensions,
            "corners": corners,
        }

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

    def _round_values(self, values, precision=6):
        """Rounds a vector/list of numeric values."""
        return [round(float(value), precision) for value in values]

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

    def _require_mapping(self, value, field_name):
        if not isinstance(value, dict):
            raise ValueError(f"'{field_name}' must be an object/dict")
        return value

    def _require_string(self, value, field_name):
        if not isinstance(value, str):
            raise ValueError(f"'{field_name}' must be a string")
        return value

    def _require_bool(self, value, field_name):
        if not isinstance(value, bool):
            raise ValueError(f"'{field_name}' must be a boolean")
        return value

    def _require_int(self, value, field_name):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"'{field_name}' must be a number")
        return int(value)

    def _require_float(self, value, field_name):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"'{field_name}' must be a number")
        return float(value)

    def _require_color(self, value, field_name, *, allow_alpha):
        expected_lengths = {3, 4} if allow_alpha else {3}
        if not isinstance(value, (list, tuple)) or len(value) not in expected_lengths:
            lengths = "3 or 4" if allow_alpha else "3"
            raise ValueError(f"'{field_name}' must be a list of {lengths} numeric values")
        return [self._require_float(component, field_name) for component in value]

    def _validate_world_settings_boundary(self, settings):
        """Rejects world payloads that try to cross into full node-graph authorship."""
        bounded_keys = {
            "world_name",
            "use_nodes",
            "color",
            "background",
            "node_tree_name",
            "node_graph_reference",
            "node_graph_handoff",
        }
        graph_keys = {"node_tree", "nodes", "links", "node_graph", "graph"}

        if graph_keys & set(settings):
            keys = ", ".join(sorted(graph_keys & set(settings)))
            raise ValueError(
                f"Unsupported world node-graph fields: {keys}. Use future node_graph tooling for graph rebuilds."
            )

        unknown_keys = set(settings) - bounded_keys
        if unknown_keys:
            keys = ", ".join(sorted(unknown_keys))
            raise ValueError(
                f"Unsupported world settings: {keys}. Allowed keys: world_name, use_nodes, color, background."
            )

    def _build_world_node_graph_reference(self, *, world_name, node_tree_name, background):
        if node_tree_name is None:
            return None
        reference = {
            "graph_type": "world",
            "owner_name": world_name,
            "node_tree_name": node_tree_name,
        }
        if background is not None:
            reference["background_node_name"] = background.get("node_name")
        return reference

    def _build_world_node_graph_handoff(self, *, world_name, node_tree_name, use_nodes, background):
        required = bool(use_nodes and node_tree_name)
        payload = {
            "required": required,
            "target_tool_family": "node_graph",
            "reason": "world_uses_nodes" if required else None,
            "world_name": world_name,
            "node_tree_name": node_tree_name,
            "supported_scene_configure_fields": [
                "world_name",
                "use_nodes",
                "color",
                "background.color",
                "background.strength",
            ],
            "unsupported_scope": (
                [
                    "arbitrary_world_nodes",
                    "custom_links",
                    "full_node_topology_rebuild",
                ]
                if required
                else []
            ),
        }
        if background is not None:
            payload["background_node_name"] = background.get("node_name")
        return payload

    def _ensure_world_background_node(self, world):
        """Returns a world Background node and creates a minimal one when absent."""
        node_tree = getattr(world, "node_tree", None)
        if node_tree is None:
            raise ValueError("World node tree is not available.")

        background_node = None
        output_node = None
        for node in getattr(node_tree, "nodes", []) or []:
            node_type = getattr(node, "type", None)
            node_idname = getattr(node, "bl_idname", None)
            if background_node is None and (node_type == "BACKGROUND" or node_idname == "ShaderNodeBackground"):
                background_node = node
            if output_node is None and (node_type == "OUTPUT_WORLD" or node_idname == "ShaderNodeOutputWorld"):
                output_node = node

        if background_node is None and hasattr(node_tree.nodes, "new"):
            background_node = node_tree.nodes.new("ShaderNodeBackground")
        if output_node is None and hasattr(node_tree.nodes, "new"):
            output_node = node_tree.nodes.new("ShaderNodeOutputWorld")

        if background_node is None:
            raise ValueError("World background node is not available.")

        if output_node is not None and hasattr(node_tree, "links") and hasattr(node_tree.links, "new"):
            try:
                node_tree.links.new(background_node.outputs["Background"], output_node.inputs["Surface"])
            except Exception:
                pass

        return background_node

    def _inspect_world_background_node(self, node_tree):
        """Extracts a compact summary of the first world background node when present."""
        for node in getattr(node_tree, "nodes", []) or []:
            node_type = getattr(node, "type", None)
            node_idname = getattr(node, "bl_idname", None)
            if node_type != "BACKGROUND" and node_idname != "ShaderNodeBackground":
                continue

            color_input = self._get_node_input_default(node, "Color")
            strength_input = self._get_node_input_default(node, "Strength")
            return {
                "node_name": getattr(node, "name", None),
                "color": self._vec_to_list(color_input) if color_input is not None else None,
                "strength": round(float(strength_input), 6) if isinstance(strength_input, (int, float)) else strength_input,
            }
        return None

    def _get_node_input_default(self, node, input_name):
        """Returns a node input default value by socket name when available."""
        for socket in getattr(node, "inputs", []) or []:
            if getattr(socket, "name", None) == input_name:
                return getattr(socket, "default_value", None)
        return None

    def _set_node_input_default(self, node, input_name, value):
        """Sets a node input default value by socket name when available."""
        for socket in getattr(node, "inputs", []) or []:
            if getattr(socket, "name", None) == input_name:
                socket.default_value = value
                return
        raise ValueError(f"World background node is missing '{input_name}' input.")
