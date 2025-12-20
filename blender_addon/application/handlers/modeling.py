import bpy
import math
from typing import List, Optional

class ModelingHandler:
    """Application service for modeling operations."""

    def create_primitive(self, primitive_type, radius=1.0, size=2.0, location=(0,0,0), rotation=(0,0,0), name=None):
        """
        [OBJECT MODE][SAFE][NON-DESTRUCTIVE] Creates a 3D primitive object.
        """
        # Normalize primitive_type to lowercase for case-insensitive matching
        ptype = primitive_type.lower()

        if ptype == "cube":
            bpy.ops.mesh.primitive_cube_add(size=size, location=location, rotation=rotation)
        elif ptype in ("sphere", "uv_sphere"):
            bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=location, rotation=rotation)
        elif ptype == "cylinder":
            bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=size, location=location, rotation=rotation)
        elif ptype == "plane":
            bpy.ops.mesh.primitive_plane_add(size=size, location=location, rotation=rotation)
        elif ptype == "cone":
            bpy.ops.mesh.primitive_cone_add(radius1=radius, depth=size, location=location, rotation=rotation)
        elif ptype == "torus":
            bpy.ops.mesh.primitive_torus_add(location=location, rotation=rotation)
        elif ptype == "monkey":
            bpy.ops.mesh.primitive_monkey_add(size=size, location=location, rotation=rotation)
        else:
            raise ValueError(f"Unknown primitive type: {primitive_type}. Valid types: cube, sphere, cylinder, plane, cone, torus, monkey")
        
        obj = bpy.context.active_object
        if name:
            obj.name = name
            
        return {"name": obj.name, "type": "MESH"}

    def transform_object(self, name, location=None, rotation=None, scale=None):
        """
        [OBJECT MODE][SAFE][NON-DESTRUCTIVE] Transforms (move, rotate, scale) an existing object.
        """
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
        """
        [OBJECT MODE][SAFE][NON-DESTRUCTIVE] Adds a modifier to an object.
        Preferred method for booleans, subdivision, mirroring (non-destructive stack).
        """
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
            # Special-case pointer properties that commonly arrive as names (strings)
            # from the MCP server.
            #
            # BooleanModifier.object expects a bpy.types.Object, but callers often
            # provide an object name. Support both `object` and `object_name`.
            if modifier_type_upper == "BOOLEAN" and "object_name" in properties and "object" not in properties:
                properties = dict(properties)
                properties["object"] = properties.pop("object_name")

            for prop, value in properties.items():
                if modifier_type_upper == "BOOLEAN" and prop == "object":
                    if value is None:
                        continue
                    if isinstance(value, str):
                        target_obj = bpy.data.objects.get(value)
                        if target_obj is None:
                            raise ValueError(
                                f"Boolean modifier target object '{value}' not found"
                            )
                        mod.object = target_obj
                    else:
                        # Allow callers to pass an actual object reference.
                        try:
                            mod.object = value
                        except Exception as e:
                            raise ValueError(f"Could not set Boolean modifier object: {e}")
                    continue

                if hasattr(mod, prop):
                    try:
                        setattr(mod, prop, value)
                    except Exception as e:
                        print(f"Warning: Could not set property {prop}: {e}")
        
        return {"modifier": mod.name}

    def apply_modifier(self, name, modifier_name):
        """
        [OBJECT MODE][DESTRUCTIVE] Applies a modifier, making its changes permanent to the mesh.
        """
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

        # Ensure we're in Object Mode (modifier_apply is an Object Mode operator).
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except Exception:
            pass

        # Blender refuses to apply disabled modifiers ("Modifier is disabled, skipping apply").
        # If the modifier is disabled in viewport/render, enable it before applying.
        mod = obj.modifiers.get(target_modifier_name)
        if mod is not None:
            if hasattr(mod, "show_viewport") and not mod.show_viewport:
                mod.show_viewport = True
            if hasattr(mod, "show_render") and not mod.show_render:
                mod.show_render = True
        
        try:
            bpy.ops.object.modifier_apply(modifier=target_modifier_name)
        except RuntimeError as e:
            raise ValueError(str(e))
        
        return {"applied_modifier": target_modifier_name, "object": name}

    def convert_to_mesh(self, name):
        """
        [OBJECT MODE][DESTRUCTIVE] Converts a non-mesh object (Curve, Text, Surface) to a mesh.
        """
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
        [OBJECT MODE][DESTRUCTIVE] Joins multiple mesh objects into a single mesh.
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
        """
        [OBJECT MODE][DESTRUCTIVE] Separates a mesh into new objects (LOOSE, SELECTED, MATERIAL).
        """
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
        """
        [OBJECT MODE][DESTRUCTIVE] Sets the origin point of an object.
        """
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
        """
        [OBJECT MODE][SAFE][READ-ONLY] Returns a list of modifiers on the object.
        """
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

    def get_modifier_data(self, object_name, modifier_name=None, include_node_tree=False):
        """
        [OBJECT MODE][READ-ONLY][SAFE] Returns full modifier properties.
        """
        if object_name not in bpy.data.objects:
            raise ValueError(f"Object '{object_name}' not found")

        obj = bpy.data.objects[object_name]

        modifiers = list(obj.modifiers)
        if modifier_name:
            modifier = obj.modifiers.get(modifier_name)
            if modifier is None:
                modifier = next((m for m in modifiers if m.name == modifier_name), None)
            if modifier is None:
                raise ValueError(f"Modifier '{modifier_name}' not found on '{object_name}'")
            modifiers = [modifier]

        result_modifiers = []
        for mod in modifiers:
            result_modifiers.append(self._serialize_modifier(mod, include_node_tree))

        return {
            "object_name": object_name,
            "modifier_count": len(result_modifiers),
            "modifiers": result_modifiers,
        }

    def _serialize_modifier(self, mod, include_node_tree):
        object_refs = []
        seen_refs = set()
        properties = {}

        for prop in sorted(mod.bl_rna.properties, key=lambda p: p.identifier):
            if prop.identifier == "rna_type":
                continue
            try:
                value = getattr(mod, prop.identifier)
            except Exception:
                continue
            properties[prop.identifier] = self._serialize_modifier_value(value, prop, object_refs, seen_refs)

        modifier_data = {
            "name": mod.name,
            "type": mod.type,
            "properties": properties,
            "object_refs": object_refs,
        }

        if include_node_tree and getattr(mod, "type", None) == "NODES":
            node_group = getattr(mod, "node_group", None)
            if node_group:
                modifier_data["node_tree"] = self._serialize_node_tree(node_group)

        return modifier_data

    def _serialize_modifier_value(self, value, prop, object_refs, seen_refs):
        if prop.type == 'POINTER':
            if value is None:
                return None
            if hasattr(value, "name"):
                key = (prop.identifier, value.name)
                if key not in seen_refs:
                    seen_refs.add(key)
                    object_refs.append({"property": prop.identifier, "object_name": value.name})
                return value.name
            return str(value)

        if prop.type == 'COLLECTION':
            items = []
            try:
                for item in value:
                    items.append(self._serialize_collection_item(item))
            except Exception:
                return []
            return items

        return self._serialize_simple_value(value)

    def _serialize_collection_item(self, item):
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

    def _serialize_node_tree(self, node_group):
        return {
            "name": node_group.name,
            "is_linked": bool(getattr(node_group, "library", None)),
            "library_path": getattr(getattr(node_group, "library", None), "filepath", None),
            "inputs": self._serialize_node_sockets(node_group, "INPUT"),
            "outputs": self._serialize_node_sockets(node_group, "OUTPUT"),
        }

    def _serialize_node_sockets(self, node_group, direction):
        sockets = []

        if direction == "INPUT" and hasattr(node_group, "inputs"):
            sockets = list(node_group.inputs)
        elif direction == "OUTPUT" and hasattr(node_group, "outputs"):
            sockets = list(node_group.outputs)
        elif hasattr(node_group, "interface"):
            items = getattr(node_group.interface, "items_tree", None) or getattr(node_group.interface, "items", None)
            if items:
                sockets = [
                    item for item in items
                    if getattr(item, "in_out", None) == direction
                ]

        return [self._serialize_node_socket(socket) for socket in sockets]

    def _serialize_node_socket(self, socket):
        data = {
            "name": getattr(socket, "name", None),
            "identifier": getattr(socket, "identifier", None),
            "socket_type": (
                getattr(socket, "bl_socket_idname", None)
                or getattr(socket, "socket_type", None)
                or getattr(socket, "type", None)
                or socket.__class__.__name__
            ),
        }

        if hasattr(socket, "default_value"):
            data["default_value"] = self._serialize_simple_value(socket.default_value)
        if hasattr(socket, "min_value"):
            data["min"] = self._serialize_simple_value(socket.min_value)
        if hasattr(socket, "max_value"):
            data["max"] = self._serialize_simple_value(socket.max_value)
        if hasattr(socket, "subtype"):
            data["subtype"] = socket.subtype

        return data

    # ==========================================================================
    # TASK-038-1: Metaball Tools
    # ==========================================================================

    def metaball_create(
        self,
        name: str = "Metaball",
        location: List = None,
        element_type: str = "BALL",
        radius: float = 1.0,
        resolution: float = 0.2,
        threshold: float = 0.6,
    ):
        """
        [OBJECT MODE][SCENE] Creates a metaball object.

        Metaballs automatically merge when close together, creating organic blob shapes.
        """
        location = location or [0, 0, 0]

        # Valid metaball element types
        valid_types = ['BALL', 'CAPSULE', 'PLANE', 'ELLIPSOID', 'CUBE']
        element_type = element_type.upper()
        if element_type not in valid_types:
            raise ValueError(f"Invalid element type: {element_type}. Valid: {valid_types}")

        # Create metaball data
        mball = bpy.data.metaballs.new(name)
        mball.resolution = resolution
        mball.threshold = threshold

        # Add the first element
        elem = mball.elements.new()
        elem.type = element_type
        elem.radius = radius
        elem.co = (0, 0, 0)  # Local position relative to object

        # Create object from metaball
        obj = bpy.data.objects.new(name, mball)
        obj.location = location

        # Link to scene
        bpy.context.collection.objects.link(obj)

        # Select and make active
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        return (
            f"Created metaball '{obj.name}' at {list(location)} "
            f"(type={element_type}, radius={radius}, resolution={resolution})"
        )

    def metaball_add_element(
        self,
        metaball_name: str,
        element_type: str = "BALL",
        location: List = None,
        radius: float = 1.0,
        stiffness: float = 2.0,
    ):
        """
        [OBJECT MODE] Adds element to existing metaball.

        Multiple elements merge together based on proximity and stiffness.
        """
        location = location or [0, 0, 0]

        if metaball_name not in bpy.data.objects:
            raise ValueError(f"Object '{metaball_name}' not found")

        obj = bpy.data.objects[metaball_name]

        if obj.type != 'META':
            raise ValueError(f"Object '{metaball_name}' is not a metaball (type: {obj.type})")

        # Valid metaball element types
        valid_types = ['BALL', 'CAPSULE', 'PLANE', 'ELLIPSOID', 'CUBE']
        element_type = element_type.upper()
        if element_type not in valid_types:
            raise ValueError(f"Invalid element type: {element_type}. Valid: {valid_types}")

        mball = obj.data

        # Add new element
        elem = mball.elements.new()
        elem.type = element_type
        elem.radius = radius
        elem.stiffness = stiffness
        elem.co = tuple(location)  # Position relative to metaball object

        element_count = len(mball.elements)

        return (
            f"Added {element_type} element to '{metaball_name}' at {location} "
            f"(radius={radius}, stiffness={stiffness}). Total elements: {element_count}"
        )

    def metaball_to_mesh(
        self,
        metaball_name: str,
        apply_resolution: bool = True,
    ):
        """
        [OBJECT MODE][DESTRUCTIVE] Converts metaball to mesh.

        Required for mesh editing operations and export.
        """
        if metaball_name not in bpy.data.objects:
            raise ValueError(f"Object '{metaball_name}' not found")

        obj = bpy.data.objects[metaball_name]

        if obj.type != 'META':
            raise ValueError(f"Object '{metaball_name}' is not a metaball (type: {obj.type})")

        # Select and make active
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        # Convert to mesh
        bpy.ops.object.convert(target='MESH')

        # Get the new mesh object
        new_obj = bpy.context.active_object
        vertex_count = len(new_obj.data.vertices)
        face_count = len(new_obj.data.polygons)

        return (
            f"Converted metaball '{metaball_name}' to mesh '{new_obj.name}' "
            f"({vertex_count} vertices, {face_count} faces)"
        )

    # ==========================================================================
    # TASK-038-6: Skin Modifier Workflow
    # ==========================================================================

    def skin_create_skeleton(
        self,
        name: str = "Skeleton",
        vertices: List = None,
        edges: List = None,
        location: List = None,
    ):
        """
        [OBJECT MODE][SCENE] Creates skeleton mesh for Skin modifier.

        Define vertices as path points, edges connect them.
        Skin modifier will create tubular mesh around this skeleton.
        """
        vertices = vertices or [[0, 0, 0], [0, 0, 1]]
        location = location or [0, 0, 0]

        # Auto-create sequential edges if not provided
        if edges is None:
            edges = [[i, i + 1] for i in range(len(vertices) - 1)]

        # Create mesh data
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(vertices, edges, [])  # vertices, edges, faces
        mesh.update()

        # Create object
        obj = bpy.data.objects.new(name, mesh)
        obj.location = location

        # Link to scene
        bpy.context.collection.objects.link(obj)

        # Select and make active
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        # Add Skin modifier
        mod = obj.modifiers.new(name="Skin", type='SKIN')

        # Add Subdivision modifier for smooth result
        subsurf = obj.modifiers.new(name="Subdivision", type='SUBSURF')
        subsurf.levels = 2
        subsurf.render_levels = 2

        return (
            f"Created skeleton '{obj.name}' with {len(vertices)} vertices, "
            f"{len(edges)} edges. Skin modifier added."
        )

    def skin_set_radius(
        self,
        object_name: str,
        vertex_index: int = None,
        radius_x: float = 0.25,
        radius_y: float = 0.25,
    ):
        """
        [EDIT MODE] Sets skin radius at vertices.

        Each vertex can have different X/Y radius for elliptical cross-sections.
        """
        if object_name not in bpy.data.objects:
            raise ValueError(f"Object '{object_name}' not found")

        obj = bpy.data.objects[object_name]

        if obj.type != 'MESH':
            raise ValueError(f"Object '{object_name}' is not a mesh")

        # Check for skin modifier
        skin_mod = None
        for mod in obj.modifiers:
            if mod.type == 'SKIN':
                skin_mod = mod
                break

        if not skin_mod:
            raise ValueError(f"Object '{object_name}' has no Skin modifier")

        # Get skin layer
        mesh = obj.data
        if not mesh.skin_vertices:
            raise ValueError(f"Object '{object_name}' has no skin data")

        skin_layer = mesh.skin_vertices[0]  # First (default) layer

        if vertex_index is not None:
            # Set specific vertex
            if vertex_index < 0 or vertex_index >= len(skin_layer.data):
                raise ValueError(
                    f"Vertex index {vertex_index} out of range "
                    f"(0 to {len(skin_layer.data) - 1})"
                )
            skin_layer.data[vertex_index].radius = (radius_x, radius_y)
            return (
                f"Set skin radius at vertex {vertex_index} to "
                f"({radius_x}, {radius_y}) on '{object_name}'"
            )
        else:
            # Set all vertices
            for sv in skin_layer.data:
                sv.radius = (radius_x, radius_y)
            return (
                f"Set skin radius for all {len(skin_layer.data)} vertices to "
                f"({radius_x}, {radius_y}) on '{object_name}'"
            )
