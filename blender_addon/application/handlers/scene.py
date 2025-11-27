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
        """Sets the interaction mode (OBJECT, EDIT, SCULPT)."""
        # Mapping generic names to Blender internal modes if needed,
        # but standard names are OBJECT, EDIT, SCULPT.
        # Blender uses 'EDIT_MESH' for meshes, but 'EDIT' in ops usually works.

        target_mode = mode.upper()

        # Map friendly names
        if target_mode == 'EDIT':
            # If it's a mesh, use EDIT, otherwise standard behavior
            pass

        if bpy.context.mode == target_mode:
            return f"Already in {target_mode} mode"

        # Ensure we have an active object for modes other than OBJECT
        if target_mode != 'OBJECT' and not bpy.context.active_object:
             raise ValueError(f"Cannot switch to {target_mode} mode: No active object.")

        try:
            bpy.ops.object.mode_set(mode=target_mode)
        except RuntimeError as e:
             # Often happens if the object type doesn't support the mode (e.g. Camera -> Edit Mode)
             raise ValueError(f"Failed to switch to {target_mode} mode. Object might not support it. Error: {e}")

        return f"Switched to {target_mode} mode"

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

        # Compute hash for change detection (SHA256 of JSON string)
        snapshot_json = json.dumps(snapshot, sort_keys=True)
        snapshot_hash = hashlib.sha256(snapshot_json.encode('utf-8')).hexdigest()

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
