import bpy

def list_objects():
    """Returns a list of objects in the scene."""
    objects = []
    for obj in bpy.context.scene.objects:
        objects.append({
            "name": obj.name,
            "type": obj.type,
            "location": [round(c, 3) for c in obj.location]
        })
    return objects

def delete_object(name):
    """Deletes an object by name."""
    if name not in bpy.data.objects:
        raise ValueError(f"Object '{name}' not found")
    
    obj = bpy.data.objects[name]
    bpy.data.objects.remove(obj, do_unlink=True)
    return {"deleted": name}

def clean_scene():
    """Deletes all geometry objects, keeping lights and cameras optional (for now deletes meshes)."""
    # Select all objects
    bpy.ops.object.select_all(action='DESELECT')
    
    to_delete = []
    for obj in bpy.context.scene.objects:
        if obj.type in ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 'POINTCLOUD', 'VOLUME']:
            to_delete.append(obj)
            
    for obj in to_delete:
        bpy.data.objects.remove(obj, do_unlink=True)
        
    return {"count": len(to_delete)}
