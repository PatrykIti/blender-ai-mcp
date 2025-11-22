import bpy
import math

class ModelingHandler:
    """Application service for modeling operations."""

    def create_primitive(self, primitive_type, radius=1.0, size=2.0, location=(0,0,0), rotation=(0,0,0)):
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
        mod = obj.modifiers.new(name=modifier_type, type=modifier_type)
        
        if properties:
            for prop, value in properties.items():
                if hasattr(mod, prop):
                    try:
                        setattr(mod, prop, value)
                    except Exception as e:
                        print(f"Warning: Could not set property {prop}: {e}")
        
        return {"modifier": mod.name}
