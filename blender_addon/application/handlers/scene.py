import bpy
import base64
import tempfile
import os
import math

class SceneHandler:
    """Application service for scene operations."""
    
    def list_objects(self):
        """Returns a list of objects in the scene."""
        objects = []
        for obj in bpy.context.scene.objects:
            objects.append({
                "name": obj.name,
                "type": obj.type,
                "location": [round(c, 3) for c in obj.location]
            })
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
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # Select all objects
        bpy.ops.object.select_all(action='DESELECT')
        
        to_delete = []
        for obj in bpy.context.scene.objects:
            if keep_lights_and_cameras:
                # Delete only geometry/helper types
                if obj.type in ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 'POINTCLOUD', 'VOLUME', 'EMPTY', 'LATTICE', 'ARMATURE']:
                    to_delete.append(obj)
            else:
                # Delete everything
                to_delete.append(obj)
                
        for obj in to_delete:
            bpy.data.objects.remove(obj, do_unlink=True)
            
        # If hard reset, also clear collections (optional but good for full reset)
        if not keep_lights_and_cameras:
             for col in bpy.data.collections:
                 if col.users == 0: # Remove orphans
                     bpy.data.collections.remove(col)

        return {"count": len(to_delete), "kept_environment": keep_lights_and_cameras}

    def duplicate_object(self, name, translation=None):
        """Duplicates an object and optionally translates it."""
        if name not in bpy.data.objects:
            raise ValueError(f"Object '{name}' not found")

        obj = bpy.data.objects[name]

        # Ensure we're in OBJECT mode
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # Deselect all, select target
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        # Duplicate
        bpy.ops.object.duplicate()
        new_obj = bpy.context.view_layer.objects.active
        
        # Translate if needed
        if translation:
             bpy.ops.transform.translate(value=translation)
             
        return {
            "original": name,
            "new_object": new_obj.name,
            "location": [round(c, 3) for c in new_obj.location]
        }

    def set_active_object(self, name):
        """Sets the active object."""
        if name not in bpy.data.objects:
             raise ValueError(f"Object '{name}' not found")

        # Ensure we're in OBJECT mode
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        obj = bpy.data.objects[name]
        bpy.ops.object.select_all(action='DESELECT')
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
            "selection_count": len(selected_names)
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
            if obj and obj.type == 'MESH':
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
        if obj.type != 'MESH':
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

    def get_viewport(self, width=1024, height=768, shading="SOLID", camera_name=None, focus_target=None):
        """Returns a base64 encoded OpenGL render of the viewport."""
        scene = bpy.context.scene
        
        # 0. Ensure Object Mode (Safety check for render operators)
        original_mode = None
        if bpy.context.active_object:
            original_mode = bpy.context.active_object.mode
            if original_mode != 'OBJECT':
                try:
                    bpy.ops.object.mode_set(mode='OBJECT')
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
                if area.type == 'VIEW_3D':
                    view_area = area
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            view_space = space
                    for region in area.regions:
                        if region.type == 'WINDOW':
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
            scene.render.image_settings.file_format = 'JPEG'
            scene.render.filepath = render_filepath_base

            # 4. Apply Shading (for OpenGL/Workbench)
            # Validate shading type
            valid_shading = {'WIREFRAME', 'SOLID', 'MATERIAL', 'RENDERED'}
            target_shading = shading.upper() if shading.upper() in valid_shading else 'SOLID'
            
            if view_space:
                view_space.shading.type = target_shading

            # 5. Handle Camera & Focus
            temp_camera_obj = None

            try:
                # Case A: Specific existing camera
                if camera_name and camera_name != "USER_PERSPECTIVE":
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
                    bpy.ops.object.select_all(action='DESELECT')
                    
                    # Select target(s) for framing
                    if focus_target:
                        if focus_target in bpy.data.objects:
                            target_obj = bpy.data.objects[focus_target]
                            target_obj.select_set(True)
                        else:
                             bpy.ops.object.select_all(action='SELECT')
                    else:
                        # No target -> Select all visible objects
                        bpy.ops.object.select_all(action='SELECT')
                    
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
                # Only attempt if we found a valid 3D View context
                if view_area and view_region:
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
                        scene.render.engine = 'BLENDER_WORKBENCH'
                        # Configure Workbench to match requested style roughly
                        scene.display.shading.light = 'STUDIO'
                        scene.display.shading.color_type = 'MATERIAL'
                        
                        if target_shading == 'WIREFRAME':
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
                        scene.render.engine = 'CYCLES'
                        scene.cycles.device = 'CPU'
                        scene.cycles.samples = 1 # Extremely fast, noisy but visible
                        scene.cycles.preview_samples = 1
                        bpy.ops.render.render(write_still=True)
                        
                        if os.path.exists(expected_output) and os.path.getsize(expected_output) > 0:
                            render_success = True
                    except Exception as e:
                        print(f"[Viewport] Cycles render failed: {e}")

                # 7. Read Result
                if not render_success:
                    raise RuntimeError("Render failed: Could not generate viewport image using OpenGL, Workbench, or Cycles.")

                b64_data = ""
                with open(expected_output, "rb") as f:
                    data = f.read()
                    b64_data = base64.b64encode(data).decode('utf-8')
                
                return b64_data

            finally:
                # 8. Cleanup Temp Files
                if os.path.exists(expected_output):
                    os.remove(expected_output)
                try:
                    os.rmdir(temp_dir)
                except:
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
                bpy.ops.object.select_all(action='DESELECT')
                for obj in original_selected:
                    try:
                        obj.select_set(True)
                    except:
                        pass 
                
                if original_active and original_active.name in bpy.data.objects:
                    bpy.context.view_layer.objects.active = original_active
                    
                # Cleanup temp camera
                if temp_camera_obj:
                    bpy.data.objects.remove(temp_camera_obj, do_unlink=True)
        finally:
            # 10. Restore Mode
            if original_mode and original_mode != 'OBJECT':
                if bpy.context.active_object:
                     try:
                         bpy.ops.object.mode_set(mode=original_mode)
                     except Exception:
                         pass

    def create_light(self, type='POINT', energy=1000.0, color=(1.0, 1.0, 1.0), location=(0.0, 0.0, 0.0), name=None):
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

    def create_camera(self, location=(0.0, -10.0, 0.0), rotation=(1.57, 0.0, 0.0), lens=50.0, clip_start=0.1, clip_end=100.0, name=None):
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

    def create_empty(self, type='PLAIN_AXES', size=1.0, location=(0.0, 0.0, 0.0), name=None):
        """Creates an empty object."""
        empty_obj = bpy.data.objects.new(name if name else "Empty", None)
        empty_obj.empty_display_type = type
        empty_obj.empty_display_size = size
        empty_obj.location = location
        
        # Link to collection
        bpy.context.collection.objects.link(empty_obj)
        
        return empty_obj.name

    def set_mode(self, mode='OBJECT'):
        """Switch Blender context mode."""
        mode = mode.upper()
        valid_modes = ['OBJECT', 'EDIT', 'SCULPT', 'VERTEX_PAINT', 'WEIGHT_PAINT', 'TEXTURE_PAINT', 'POSE']

        if mode not in valid_modes:
            raise ValueError(f"Invalid mode '{mode}'. Valid: {valid_modes}")

        current_mode = bpy.context.mode

        if current_mode == mode or current_mode.startswith(mode):
            return f"Already in {mode} mode"

        active_obj = bpy.context.active_object
        
        if mode != 'OBJECT' and not active_obj:
             raise ValueError(f"Cannot enter {mode} mode: no active object")

        # Validate object type for specific modes
        if mode == 'EDIT':
            valid_types = ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'LATTICE', 'ARMATURE']
            if active_obj.type not in valid_types:
                raise ValueError(
                    f"Cannot enter {mode} mode: active object '{active_obj.name}' "
                    f"is type '{active_obj.type}'. Supported types: {', '.join(valid_types)}"
                )
        elif mode == 'SCULPT':
             if active_obj.type != 'MESH':
                 raise ValueError(f"Cannot enter SCULPT mode: active object '{active_obj.name}' is type '{active_obj.type}'. Only MESH supported.")
        elif mode == 'POSE':
             if active_obj.type != 'ARMATURE':
                 raise ValueError(f"Cannot enter POSE mode: active object '{active_obj.name}' is type '{active_obj.type}'. Only ARMATURE supported.")

        bpy.ops.object.mode_set(mode=mode)
        return f"Switched to {mode} mode"

    def snapshot_state(self, include_mesh_stats=False, include_materials=False):
        """Captures a lightweight JSON snapshot of the scene state."""
        import json
        import hashlib
        from datetime import datetime

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
                "visible": not obj.hide_get(),
                "selected": obj.select_get(),
                "collections": [col.name for col in obj.users_collection]
            }

            # Optional: Include modifiers info
            if obj.modifiers:
                obj_data["modifiers"] = [
                    {"name": mod.name, "type": mod.type}
                    for mod in obj.modifiers
                ]

            # Optional: Include mesh stats
            if include_mesh_stats and obj.type == 'MESH':
                mesh_stats = self._gather_mesh_stats(obj)
                if mesh_stats:
                    obj_data["mesh_stats"] = mesh_stats

            # Optional: Include material info
            if include_materials and obj.material_slots:
                obj_data["materials"] = [
                    slot.material.name if slot.material else None
                    for slot in obj.material_slots
                ]

            objects_data.append(obj_data)

        # Build snapshot payload
        snapshot = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "object_count": len(objects_data),
            "objects": objects_data,
            "active_object": bpy.context.active_object.name if bpy.context.active_object else None,
            "mode": getattr(bpy.context, "mode", "UNKNOWN")
        }

        # Compute hash for change detection (SHA256 of scene state, excluding timestamp)
        # This ensures identical scenes produce identical hashes
        state_for_hash = {
            "object_count": snapshot["object_count"],
            "objects": snapshot["objects"],
            "active_object": snapshot["active_object"],
            "mode": snapshot["mode"]
        }
        state_json = json.dumps(state_for_hash, sort_keys=True)
        snapshot_hash = hashlib.sha256(state_json.encode('utf-8')).hexdigest()

        # Return snapshot with hash
        return {
            "hash": snapshot_hash,
            "snapshot": snapshot
        }

    def inspect_mesh_topology(self, object_name, detailed=False):
        """Reports detailed topology stats for a given mesh."""
        if object_name not in bpy.data.objects:
             raise ValueError(f"Object '{object_name}' not found")
        
        obj = bpy.data.objects[object_name]
        if obj.type != 'MESH':
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
            if not hasattr(obj, 'material_slots') or len(obj.material_slots) == 0:
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
                    "is_empty": mat_name is None
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
            "slots": slot_data
        }

    def inspect_modifiers(self, object_name=None, include_disabled=True):
        """Audits modifier stacks for a specific object or the entire scene."""
        result = {
            "object_count": 0,
            "modifier_count": 0,
            "objects": []
        }

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
                if mod.type == 'SUBSURF':
                    mod_info["levels"] = mod.levels
                    mod_info["render_levels"] = mod.render_levels
                elif mod.type == 'BEVEL':
                    mod_info["width"] = mod.width
                    mod_info["segments"] = mod.segments
                    mod_info["limit_method"] = mod.limit_method
                elif mod.type == 'MIRROR':
                    mod_info["use_axis"] = [mod.use_axis[0], mod.use_axis[1], mod.use_axis[2]]
                    mod_info["mirror_object"] = mod.mirror_object.name if mod.mirror_object else None
                elif mod.type == 'BOOLEAN':
                    mod_info["operation"] = mod.operation
                    mod_info["object"] = mod.object.name if mod.object else None
                    mod_info["solver"] = mod.solver
                elif mod.type == 'ARRAY':
                    mod_info["count"] = mod.count
                    mod_info["use_relative_offset"] = mod.use_relative_offset
                    mod_info["use_constant_offset"] = mod.use_constant_offset
                elif mod.type == 'SOLIDIFY':
                    mod_info["thickness"] = mod.thickness
                    mod_info["offset"] = mod.offset

                modifiers.append(mod_info)

            if modifiers:
                result["objects"].append({
                    "name": obj.name,
                    "modifiers": modifiers
                })
                result["modifier_count"] += len(modifiers)
                result["object_count"] += 1

        return result

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
        from mathutils import Matrix, Vector, Euler

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
        view_area = None
        rv3d = None

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                view_area = area
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
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
        rot_h = Matrix.Rotation(h_rad, 4, 'Z')
        # Vertical rotation (around local X axis)
        rot_v = Matrix.Rotation(v_rad, 4, 'X')

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
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        rv3d = space.region_3d
                        break
                break

        if not rv3d:
            return "No 3D viewport found. Camera focus requires an active 3D view."

        # Calculate object center and size from bounding box
        if obj.type == 'MESH' and obj.data:
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
                elif hasattr(value, '__iter__') and not isinstance(value, str):
                    # Convert vectors/arrays to lists
                    try:
                        properties[key] = list(value)
                    except Exception:
                        properties[key] = str(value)
                else:
                    properties[key] = str(value)
        except Exception as e:
            raise ValueError(f"Failed to read custom properties: {e}")

        return {
            "object_name": object_name,
            "property_count": len(properties),
            "properties": properties
        }

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
            node = {
                "name": obj.name,
                "type": obj.type,
                "children": []
            }

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

            return {
                "root": hierarchy,
                "parent_chain": parent_chain
            }
        else:
            # Get all root objects (no parent)
            roots = []
            for obj in sorted(bpy.context.scene.objects, key=lambda o: o.name):
                if obj.parent is None:
                    roots.append(build_hierarchy(obj, include_transforms))

            return {
                "root_count": len(roots),
                "hierarchy": roots
            }

    def get_bounding_box(self, object_name, world_space=True):
        """Gets bounding box corners for an object."""
        from mathutils import Vector

        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise ValueError(f"Object '{object_name}' not found")

        # Get bounding box corners
        bbox = obj.bound_box

        if world_space:
            # Transform to world space
            corners = [obj.matrix_world @ Vector(corner) for corner in bbox]
        else:
            corners = [Vector(corner) for corner in bbox]

        # Calculate min/max
        min_corner = [
            min(c[0] for c in corners),
            min(c[1] for c in corners),
            min(c[2] for c in corners)
        ]
        max_corner = [
            max(c[0] for c in corners),
            max(c[1] for c in corners),
            max(c[2] for c in corners)
        ]

        # Calculate center and dimensions
        center = [
            (min_corner[0] + max_corner[0]) / 2,
            (min_corner[1] + max_corner[1]) / 2,
            (min_corner[2] + max_corner[2]) / 2
        ]
        dimensions = [
            max_corner[0] - min_corner[0],
            max_corner[1] - min_corner[1],
            max_corner[2] - min_corner[2]
        ]

        return {
            "object_name": object_name,
            "world_space": world_space,
            "min": [round(v, 4) for v in min_corner],
            "max": [round(v, 4) for v in max_corner],
            "center": [round(v, 4) for v in center],
            "dimensions": [round(v, 4) for v in dimensions],
            "corners": [[round(c, 4) for c in corner] for corner in corners]
        }

    def get_origin_info(self, object_name):
        """Gets origin (pivot point) information for an object."""
        from mathutils import Vector

        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise ValueError(f"Object '{object_name}' not found")

        # Origin is at obj.location in world space
        origin = obj.location.copy()

        # Calculate bounding box center for comparison
        bbox = obj.bound_box
        corners = [obj.matrix_world @ Vector(corner) for corner in bbox]
        bbox_center = sum(corners, Vector()) / 8

        # Calculate offset from bbox center
        offset_from_center = origin - bbox_center

        # Determine origin type (approximate)
        origin_type = "CUSTOM"
        offset_magnitude = offset_from_center.length

        if offset_magnitude < 0.001:
            origin_type = "CENTER"
        else:
            # Check if at bottom center
            min_z = min(c[2] for c in corners)
            if abs(origin[2] - min_z) < 0.001 and abs(offset_from_center[0]) < 0.001 and abs(offset_from_center[1]) < 0.001:
                origin_type = "BOTTOM_CENTER"

        return {
            "object_name": object_name,
            "origin_world": [round(v, 4) for v in origin],
            "bbox_center": [round(v, 4) for v in bbox_center],
            "offset_from_center": [round(v, 4) for v in offset_from_center],
            "estimated_type": origin_type
        }
