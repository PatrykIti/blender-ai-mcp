import bpy
import math
from typing import List

class ModelingHandler:
    """Application service for modeling operations."""

    def create_primitive(self, primitive_type, radius=1.0, size=2.0, location=(0,0,0), rotation=(0,0,0), name=None):
        if primitive_type == "Cube":
            bpy.ops.mesh.primitive_cube_add(size=size, location=location, rotation=rotation)
        elif primitive_type == "Sphere":
            bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=location, rotation=rotation)
        elif primitive_type == "Cylinder":
            bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=size, location=location, rotation=rotation)
        elif primitive_type == "Plane":
            bpy.ops.mesh.primitive_plane_add(size=size, location=location, rotation=rotation)
        elif primitive_type == "Cone":
            bpy.ops.mesh.primitive_cone_add(radius1=radius, depth=size, location=location, rotation=rotation)
        elif primitive_type == "Torus":
            bpy.ops.mesh.primitive_torus_add(location=location, rotation=rotation)
        elif primitive_type == "Monkey":
            bpy.ops.mesh.primitive_monkey_add(size=size, location=location, rotation=rotation)
        else:
            raise ValueError(f"Unknown primitive type: {primitive_type}")
        
        obj = bpy.context.active_object
        if name:
            obj.name = name
            
        return {"name": obj.name, "type": "MESH"}

    def transform_object(self, name, location=None, rotation=None, scale=None):
        if name not in bpy.data.objects:
            raise ValueError(f"Object '{name}' not found")
        
        obj = bpy.data.objects[name]
        
        if location:
            obj.location = location
        if rotation:
            # Convert degrees to radians if needed, but usually API expects radians. 
            # Let's assume input is in radians or handle it. 
            # Standard bpy uses Euler (radians). 
            # If we want to be user friendly for LLM, maybe accept degrees? 
            # For now, let's stick to standard vector inputs.
            obj.rotation_euler = rotation
        if scale:
            obj.scale = scale
            
        return {"name": name, "location": list(obj.location)}

    def add_modifier(self, name, modifier_type, properties=None):
        if name not in bpy.data.objects:
            raise ValueError(f"Object '{name}' not found")
        
        obj = bpy.data.objects[name]
        
        # Normalize modifier type to uppercase (Blender convention: SUBSURF, BEVEL, etc.)
        modifier_type_upper = modifier_type.upper()
        
        try:
            mod = obj.modifiers.new(name=modifier_type, type=modifier_type_upper)
        except TypeError:
             # Fallback if exact type name provided was correct but not upper (rare) or invalid
             raise ValueError(f"Invalid modifier type: '{modifier_type}'")
        except Exception as e:
             raise ValueError(f"Could not create modifier '{modifier_type}': {str(e)}")
        
        if properties:
            for prop, value in properties.items():
                if hasattr(mod, prop):
                    try:
                        setattr(mod, prop, value)
                    except Exception as e:
                        print(f"Warning: Could not set property {prop}: {e}")
        
        return {"modifier": mod.name}

    def apply_modifier(self, name, modifier_name):
        """Applies a modifier to an object."""
        if name not in bpy.data.objects:
            raise ValueError(f"Object '{name}' not found")
        
        obj = bpy.data.objects[name]
        
        target_modifier_name = modifier_name
        
        if modifier_name not in obj.modifiers:
            # Case-insensitive fallback lookup
            # e.g. AI asks for "bevel", but modifier is named "Bevel" or "BEVEL"
            found = None
            for m in obj.modifiers:
                if m.name.upper() == modifier_name.upper():
                    found = m.name
                    break
            
            if found:
                target_modifier_name = found
            else:
                raise ValueError(f"Modifier '{modifier_name}' not found on object '{name}'")
            
        # Select the object and make it active for the operator to work
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        bpy.ops.object.modifier_apply(modifier=target_modifier_name)
        
        return {"applied_modifier": target_modifier_name, "object": name}

    def convert_to_mesh(self, name):
        """Converts a non-mesh object (e.g., Curve, Text, Surface) to a mesh."""
        if name not in bpy.data.objects:
            raise ValueError(f"Object '{name}' not found")
        
        obj = bpy.data.objects[name]
        
        if obj.type == 'MESH':
            return {"name": name, "type": "MESH", "status": "already_mesh"}

        # Select the object and make it active
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        # Convert to mesh
        try:
            bpy.ops.object.convert(target='MESH')
        except RuntimeError as e:
            raise ValueError(f"Failed to convert object '{name}' to mesh: {str(e)}")
            
        return {"name": obj.name, "type": "MESH", "status": "converted"}

    def join_objects(self, object_names):
        """
        Joins multiple mesh objects into a single mesh object.
        The LAST object in the list becomes the Active Object (Base) and retains its name/properties.
        """
        if not object_names:
            raise ValueError("No objects provided for joining.")
            
        # Validate all objects exist
        objects_to_join = []
        for name in object_names:
            if name not in bpy.data.objects:
                raise ValueError(f"Object '{name}' not found")
            objects_to_join.append(bpy.data.objects[name])
            
        # Deselect all first
        bpy.ops.object.select_all(action='DESELECT')
        
        # Select all objects to be joined
        for obj in objects_to_join:
            obj.select_set(True)
            
        # The last selected object becomes the active one for joining
        bpy.context.view_layer.objects.active = objects_to_join[-1]
        
        try:
            bpy.ops.object.join()
        except RuntimeError as e:
            raise ValueError(f"Failed to join objects: {str(e)}")
            
        # The active object after join is the new combined object
        joined_obj = bpy.context.active_object
        return {"name": joined_obj.name, "joined_count": len(object_names)}

    def separate_object(self, name, type="LOOSE") -> List[str]:
        """Separates a mesh object into new objects based on type (LOOSE, SELECTED, MATERIAL)."""
        if name not in bpy.data.objects:
            raise ValueError(f"Object '{name}' not found")
        
        obj = bpy.data.objects[name]
        
        valid_types = ['LOOSE', 'SELECTED', 'MATERIAL']
        separate_type = type.upper()
        if separate_type not in valid_types:
            raise ValueError(f"Invalid separation type: '{type}'. Must be one of {valid_types}")
            
        if obj.type != 'MESH':
            raise ValueError(f"Object '{name}' is not a mesh. Can only separate mesh objects.")

        # Get current objects in scene to identify new ones later
        initial_objects = set(bpy.context.scene.objects)

        # Select the object and make it active
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        # Enter Edit Mode
        bpy.ops.object.mode_set(mode='EDIT')
        
        try:
            bpy.ops.mesh.separate(type=separate_type)
        except RuntimeError as e:
            bpy.ops.object.mode_set(mode='OBJECT') # Ensure we exit edit mode on error
            raise ValueError(f"Failed to separate object '{name}' by type '{type}': {str(e)}")
            
        # Exit Edit Mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # Identify newly created objects
        current_objects = set(bpy.context.scene.objects)
        new_objects = current_objects - initial_objects
        
        new_object_names = [o.name for o in new_objects]
        return {"separated_objects": new_object_names, "original_object": name}

    def set_origin(self, name, type):
        """Sets the origin point of an object using Blender's origin_set operator types."""
        if name not in bpy.data.objects:
            raise ValueError(f"Object '{name}' not found")
        
        obj = bpy.data.objects[name]
        
        valid_types = [
            'GEOMETRY_ORIGIN',        # Geometry to Origin
            'ORIGIN_GEOMETRY',        # Origin to Geometry
            'ORIGIN_CURSOR',          # Origin to 3D Cursor
            'ORIGIN_CENTER_OF_MASS',  # Origin to Center of Mass (Surface)
            'ORIGIN_CENTER_OF_VOLUME' # Origin to Center of Mass (Volume)
        ]
        
        origin_type_upper = type.upper()
        if origin_type_upper not in valid_types:
            # Provide a helpful error message with valid options
            raise ValueError(f"Invalid origin type: '{type}'. Must be one of {valid_types}")

        # Select the object and make it active
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        try:
            bpy.ops.object.origin_set(type=origin_type_upper)
        except RuntimeError as e:
            raise ValueError(f"Failed to set origin for object '{name}' with type '{type}': {str(e)}")
            
        return {"object": name, "origin_type": origin_type_upper, "status": "success"}

    def get_modifiers(self, name):
        """Returns a list of modifiers on the object."""
        if name not in bpy.data.objects:
            raise ValueError(f"Object '{name}' not found")
        
        obj = bpy.data.objects[name]
        modifiers_list = []
        
        for mod in obj.modifiers:
            modifiers_list.append({
                "name": mod.name,
                "type": mod.type,
                "show_viewport": mod.show_viewport,
                "show_render": mod.show_render
            })
            
        return modifiers_list
