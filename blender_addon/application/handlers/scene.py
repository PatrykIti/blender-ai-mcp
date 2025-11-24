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
                    # If switching fails, we might not be able to render correctly, but proceed
                    pass

        try:
            # 1. Locate 3D View for context overrides
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

            if not view_area or not view_space or not view_region:
                 # Fallback if running headless or strange UI layout, but for OpenGL render we really need a View3D
                 raise RuntimeError("Could not find a valid 3D View area in Blender context.")

            # 2. Save State (Render settings, Camera, Selection, Shading)
            original_res_x = scene.render.resolution_x
            original_res_y = scene.render.resolution_y
            original_filepath = scene.render.filepath
            original_camera = scene.camera
            original_shading_type = view_space.shading.type
            original_active = bpy.context.view_layer.objects.active
            original_selected = [obj for obj in bpy.context.view_layer.objects if obj.select_get()]

            # 3. Setup Render Settings
            scene.render.resolution_x = width
            scene.render.resolution_y = height
            
            # 4. Apply Shading
            # Validate shading type
            valid_shading = {'WIREFRAME', 'SOLID', 'MATERIAL', 'RENDERED'}
            if shading.upper() in valid_shading:
                view_space.shading.type = shading.upper()
            else:
                 # Default fallback or warning? Let's stick to current if invalid
                 pass

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
                            # Fallback: if target invalid, select all
                             bpy.ops.object.select_all(action='SELECT')
                    else:
                        # No target -> Select all visible objects
                        bpy.ops.object.select_all(action='SELECT')
                    
                    # Frame the camera to selection
                    # We need proper context override for 'view3d.camera_to_view_selected'
                    with bpy.context.temp_override(area=view_area, region=view_region):
                        bpy.ops.view3d.camera_to_view_selected()

                # 6. Render
                fd, temp_path = tempfile.mkstemp(suffix=".jpg")
                os.close(fd)
                scene.render.filepath = temp_path

                with bpy.context.temp_override(area=view_area, region=view_region):
                     bpy.ops.render.opengl(write_still=True)

                # 7. Read Result
                b64_data = ""
                if os.path.exists(temp_path):
                    with open(temp_path, "rb") as f:
                        data = f.read()
                        b64_data = base64.b64encode(data).decode('utf-8')
                    os.remove(temp_path)
                
                return b64_data

            finally:
                # 8. Restore State
                scene.render.resolution_x = original_res_x
                scene.render.resolution_y = original_res_y
                scene.render.filepath = original_filepath
                scene.camera = original_camera
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
            # 9. Restore Mode
            if original_mode and original_mode != 'OBJECT':
                # Only switch back if we successfully switched away and object still exists
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
