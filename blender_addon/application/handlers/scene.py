import bpy

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
