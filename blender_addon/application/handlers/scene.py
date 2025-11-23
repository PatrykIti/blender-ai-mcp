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

    def get_viewport(self, width=1024, height=768):
        """Returns a base64 encoded OpenGL render of the viewport."""
        # Save current settings
        scene = bpy.context.scene
        original_res_x = scene.render.resolution_x
        original_res_y = scene.render.resolution_y
        original_filepath = scene.render.filepath
        
        # Setup temp settings
        scene.render.resolution_x = width
        scene.render.resolution_y = height
        
        # Handle Camera
        camera_created = False
        original_camera = scene.camera
        
        # Try to find a 3D View area for context override
        view_area = None
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                view_area = area
                break

        if not scene.camera:
            # Create temp camera
            bpy.ops.object.camera_add()
            cam_obj = bpy.context.active_object
            scene.camera = cam_obj
            camera_created = True
            
            # Position camera to see everything
            # We select all visible objects to frame them
            bpy.ops.object.select_all(action='SELECT')
            
            if view_area:
                with bpy.context.temp_override(area=view_area, region=view_area.regions[0]):
                     bpy.ops.view3d.camera_to_view_selected()
            else:
                 # Fallback if no 3D view found (should not happen in standard UI, but possible in some modes)
                 cam_obj.location = (15, -15, 12)
                 # Point roughly to center (approximate look_at logic)
                 cam_obj.rotation_euler = (math.radians(55), 0, math.radians(45))
        
        # Render OpenGL
        fd, temp_path = tempfile.mkstemp(suffix=".jpg")
        os.close(fd)
        
        scene.render.filepath = temp_path
        
        # Render
        # If we found a view area, use it to get a "nice" viewport render (Solid/Material mode)
        # Otherwise standard render
        if view_area:
             with bpy.context.temp_override(area=view_area):
                 bpy.ops.render.opengl(write_still=True)
        else:
             bpy.ops.render.opengl(write_still=True)
        
        # Read back
        b64_data = ""
        if os.path.exists(temp_path):
            with open(temp_path, "rb") as f:
                data = f.read()
                b64_data = base64.b64encode(data).decode('utf-8')
            os.remove(temp_path)
        
        # Restore settings
        scene.render.resolution_x = original_res_x
        scene.render.resolution_y = original_res_y
        scene.render.filepath = original_filepath
        
        if camera_created:
            bpy.data.objects.remove(scene.camera, do_unlink=True)
            scene.camera = original_camera
            
        return b64_data
