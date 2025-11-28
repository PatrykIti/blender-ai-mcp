import bpy
import bmesh

class MeshHandler:
    """Application service for Edit Mode mesh operations."""

    def _ensure_edit_mode(self):
        """
        Ensures the active object is a Mesh and in Edit Mode.
        Returns tuple (obj, previous_mode).
        """
        obj = bpy.context.active_object
        if not obj or obj.type != 'MESH':
            raise ValueError("Active object must be a Mesh.")
        
        previous_mode = obj.mode
        
        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
        
        return obj, previous_mode

    def _get_bmesh(self):
        """Returns the BMesh of the active object."""
        obj, _ = self._ensure_edit_mode()
        bm = bmesh.from_edit_mesh(obj.data)
        return bm

    def select_all(self, deselect=False):
        """
        [EDIT MODE][SELECTION-BASED][SAFE] Selects or deselects all geometry.
        """
        self._ensure_edit_mode()
        action = 'DESELECT' if deselect else 'SELECT'
        bpy.ops.mesh.select_all(action=action)
        return "Deselected all" if deselect else "Selected all"

    def delete_selected(self, type='VERT'):
        """
        [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Deletes selected elements.
        Type: VERT, EDGE, FACE.
        """
        # Using bmesh for deletion is safer when mixing with other bmesh ops
        bm = self._get_bmesh()
        
        # Ensure lookups
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        
        to_delete = []
        
        # Map string type to bmesh sequence
        if type == 'VERT':
            to_delete = [v for v in bm.verts if v.select]
        elif type == 'EDGE':
            to_delete = [e for e in bm.edges if e.select]
        elif type == 'FACE':
            to_delete = [f for f in bm.faces if f.select]
        else:
            # Fallback for other types if needed, or raise error
            raise ValueError(f"Invalid delete type: {type}. Must be VERT, EDGE, or FACE.")
            
        count = len(to_delete)
        
        # Execute delete
        # context: VERTS, EDGES, FACES, EDGES_FACES, FACES_KEEP_BOUNDARY etc.
        # For simplicity mapping VERT->VERTS, EDGE->EDGES, FACE->FACES
        context_map = {
            'VERT': 'VERTS', 
            'EDGE': 'EDGES', 
            'FACE': 'FACES'
        }
        
        bmesh.ops.delete(bm, geom=to_delete, context=context_map.get(type, 'VERTS'))
        
        # Update mesh
        bmesh.update_edit_mesh(bpy.context.active_object.data)
        
        return f"Deleted {count} selected {type}(s)"

    def select_by_index(self, indices, type='VERT', selection_mode='SET'):
        """
        [EDIT MODE][SELECTION-BASED][SAFE] Select geometry elements by index.
        Uses BMesh for precise 0-based indexing.
        
        Args:
            type: 'VERT', 'EDGE', 'FACE'
            selection_mode: 'SET' (replace), 'ADD' (extend), 'SUBTRACT' (deselect)
        """
        # Handle SET mode (exclusive selection)
        if selection_mode == 'SET':
            bpy.ops.mesh.select_all(action='DESELECT')

        bm = self._get_bmesh()
        
        # Ensure lookups table is current
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        
        target_seq = None
        if type == 'VERT':
            target_seq = bm.verts
        elif type == 'EDGE':
            target_seq = bm.edges
        elif type == 'FACE':
            target_seq = bm.faces
        else:
            raise ValueError(f"Invalid type: {type}. Must be VERT, EDGE, or FACE.")
            
        count = 0
        target_state = False if selection_mode == 'SUBTRACT' else True
        
        for i in indices:
            if 0 <= i < len(target_seq):
                # Set select state
                target_seq[i].select = target_state
                count += 1
        
        # Flush selection to ensure consistent state
        bmesh.update_edit_mesh(bpy.context.active_object.data)
        
        action_desc = "Deselected" if selection_mode == 'SUBTRACT' else "Selected"
        return f"{action_desc} {count} {type}(s) (Mode: {selection_mode})"

    def extrude_region(self, move=None):
        """
        Extrudes selected region.
        WARNING: If 'move' is None, geometry is created in-place (overlapping).
        Always provide 'move' or follow up with a transform.
        """
        self._ensure_edit_mode()
        
        # Use built-in operator which handles context well for simple extrusion
        # Default mode is REGION which is what 'E' key does
        args = {}
        if move:
            args['TRANSFORM_OT_translate'] = {"value": move}
            
        # We call extrude_region_move. 
        # Note: Passing transform args to a macro operator like this via python is sometimes tricky.
        # Alternatively, we call extrude, then translate.
        
        bpy.ops.mesh.extrude_region_move(
            MESH_OT_extrude_region={"use_normal_flip":False, "use_dissolve_ortho_edges":False, "mirror":False}, 
            TRANSFORM_OT_translate={"value": move if move else (0,0,0)}
        )
        
        return "Extruded region"

    def fill_holes(self):
        """
        [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Fills holes by creating faces from selected edges.
        Equivalent to 'F' key. Recalculates normals automatically.
        """
        self._ensure_edit_mode()
        # F key behavior
        # Context: Selected edges/vertices
        bpy.ops.mesh.edge_face_add()
        
        # Recalculate normals to prevent invisible faces (backface culling issues)
        bpy.ops.mesh.select_all(action='SELECT') # Select all to ensure consistent normals across whole mesh
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.mesh.select_all(action='DESELECT') # Cleanup selection
        
        return "Filled holes and recalculated normals"

    def bevel(self, offset=0.1, segments=1, profile=0.5, affect='EDGES'):
        """
        [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Bevels selected geometry.
        """
        self._ensure_edit_mode()
        # bpy.ops.mesh.bevel works on selection
        bpy.ops.mesh.bevel(
            offset=offset, 
            segments=segments, 
            profile=profile, 
            affect=affect # 'VERTICES' or 'EDGES'
        )
        return f"Bevel applied (offset={offset}, segments={segments})"

    def loop_cut(self, number_cuts=1, smoothness=0.0):
        """
        Adds cuts to the mesh geometry.
        IMPORTANT: This uses 'subdivide' on SELECTED edges.
        You MUST select edges perpendicular to the desired cut direction first.
        """
        self._ensure_edit_mode()
        
        try:
            # This is highly likely to fail in headless/background mode without correct override
            # We can try to override the context if we have a 3D view (which we check for get_viewport)
            # But identifying the *ring* to cut is impossible without an edge index target.
            
            # ALTERNATIVE: Subdivide selected edges.
            # If edges are selected, subdivide cuts them.
            bpy.ops.mesh.subdivide(number_cuts=number_cuts, smoothness=smoothness)
            return f"Subdivided selected geometry (cuts={number_cuts})"
            
        except Exception as e:
            return f"Failed to loop cut: {e}"

    def inset(self, thickness=0.0, depth=0.0):
        """
        [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Insets selected faces.
        """
        self._ensure_edit_mode()
        bpy.ops.mesh.inset(thickness=thickness, depth=depth)
        return f"Inset applied (thickness={thickness}, depth={depth})"

    def boolean(self, operation='DIFFERENCE', solver='EXACT'):
        """
        [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Boolean operation on selected geometry.
        Formula: Unselected - Selected (for DIFFERENCE).
        TIP: For object-level booleans, prefer 'modeling_add_modifier(BOOLEAN)' (safer).
        
        Workflow:
          1. Select 'Cutter' geometry.
          2. Deselect 'Base' geometry.
          3. Run tool.
        """
        self._ensure_edit_mode()
        bpy.ops.mesh.intersect_boolean(operation=operation, solver=solver)
        return f"Boolean {operation} applied"

    def merge_by_distance(self, distance=0.001):
        """
        [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Merges vertices within threshold distance.
        Useful for cleaning up geometry after imports or boolean ops.
        """
        self._ensure_edit_mode()
        # Assumes we want to clean up whole selection or everything?
        # Usually 'remove doubles' implies everything selected.
        # Let's rely on current selection.
        bpy.ops.mesh.remove_doubles(threshold=distance)
        return f"Merged vertices by distance {distance}"

    def subdivide(self, number_cuts=1, smoothness=0.0):
        """
        [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Subdivides selected geometry.
        """
        self._ensure_edit_mode()
        bpy.ops.mesh.subdivide(number_cuts=number_cuts, smoothness=smoothness)
        return f"Subdivided selected geometry (cuts={number_cuts})"

    def smooth_vertices(self, iterations=1, factor=0.5):
        """
        [EDIT MODE][SELECTION-BASED][NON-DESTRUCTIVE] Smooths selected vertices.
        Uses Laplacian smoothing algorithm.
        """
        obj, previous_mode = self._ensure_edit_mode()
        
        bm = bmesh.from_edit_mesh(obj.data)
        selected_verts = [v for v in bm.verts if v.select]
        
        if not selected_verts:
            # Restore mode before raising error? Or just raise?
            # Ideally restore, but if we fail fast...
            # The context is already changed. Let's try to be nice.
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError("No vertices selected")
        
        vert_count = len(selected_verts)
        
        bpy.ops.mesh.vertices_smooth(factor=factor, repeat=iterations)
        
        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)
        
        return f"Smoothed {vert_count} vertices ({iterations} iterations, {factor:.2f} factor)"

    def flatten_vertices(self, axis):
        """
        [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Flattens selected vertices to plane.
        Aligns vertices perpendicular to chosen axis using scale-to-zero transform.
        """
        obj, previous_mode = self._ensure_edit_mode()
        
        bm = bmesh.from_edit_mesh(obj.data)
        selected_verts = [v for v in bm.verts if v.select]
        
        if not selected_verts:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError("No vertices selected")
        
        vert_count = len(selected_verts)
        
        axis = axis.upper()
        if axis not in ['X', 'Y', 'Z']:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError(f"Invalid axis '{axis}'. Must be X, Y, or Z")
        
        constraint_map = {
            "X": (True, False, False),
            "Y": (False, True, False),
            "Z": (False, False, True)
        }
        
        constraint = constraint_map[axis]
        scale_value = [1.0, 1.0, 1.0]
        for i, constrained in enumerate(constraint):
            if constrained:
                scale_value[i] = 0.0
        
        bpy.ops.transform.resize(
            value=tuple(scale_value),
            constraint_axis=constraint,
            orient_type='GLOBAL'
        )

        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)

        return f"Flattened {vert_count} vertices along {axis} axis"

    def list_groups(self, object_name, group_type='VERTEX'):
        """
        [MESH][SAFE][READ-ONLY] Lists vertex/face groups defined on mesh object.

        Args:
            object_name: Name of the mesh object to inspect
            group_type: Type of groups to list ('VERTEX' or 'FACE')

        Returns:
            Dict with group information including name, index, member_count, and flags
        """
        if object_name not in bpy.data.objects:
            raise ValueError(f"Object '{object_name}' not found")

        obj = bpy.data.objects[object_name]

        if obj.type != 'MESH':
            raise ValueError(f"Object '{object_name}' is not a MESH (type: {obj.type})")

        group_type = group_type.upper()

        if group_type == 'VERTEX':
            groups_data = []

            for idx, vg in enumerate(obj.vertex_groups):
                # Count assigned vertices by iterating through mesh vertices
                assigned_count = 0
                for v in obj.data.vertices:
                    try:
                        # Check if vertex is in this group
                        if vg.index in [g.group for g in v.groups]:
                            assigned_count += 1
                    except:
                        pass

                group_info = {
                    "name": vg.name,
                    "index": vg.index,
                    "member_count": assigned_count,
                    "lock_weight": vg.lock_weight,
                }
                groups_data.append(group_info)

            return {
                "object_name": object_name,
                "group_type": "VERTEX",
                "group_count": len(groups_data),
                "groups": groups_data
            }

        elif group_type == 'FACE':
            # Face maps were removed in Blender 3.0+
            # Check if face_maps attribute exists
            if hasattr(obj, 'face_maps'):
                groups_data = []
                for fm in obj.face_maps:
                    group_info = {
                        "name": fm.name,
                        "index": fm.index,
                        "member_count": 0  # Face maps don't track count directly
                    }
                    groups_data.append(group_info)

                return {
                    "object_name": object_name,
                    "group_type": "FACE",
                    "group_count": len(groups_data),
                    "groups": groups_data,
                    "note": "Face maps are deprecated in Blender 3.0+"
                }
            else:
                # Try using face attributes (Blender 3.0+)
                # Face attributes are stored in obj.data.attributes
                face_attributes = [attr for attr in obj.data.attributes if attr.domain == 'FACE']

                if not face_attributes:
                    return {
                        "object_name": object_name,
                        "group_type": "FACE",
                        "group_count": 0,
                        "groups": [],
                        "note": "No face attributes found. Face maps were deprecated in Blender 3.0+. Use vertex groups or custom attributes instead."
                    }

                groups_data = []
                for attr in face_attributes:
                    group_info = {
                        "name": attr.name,
                        "data_type": attr.data_type,
                        "domain": attr.domain
                    }
                    groups_data.append(group_info)

                return {
                    "object_name": object_name,
                    "group_type": "FACE",
                    "group_count": len(groups_data),
                    "groups": groups_data,
                    "note": "Showing face-domain attributes (Blender 3.0+ replacement for face maps)"
                }
        else:
            raise ValueError(f"Invalid group_type '{group_type}'. Must be 'VERTEX' or 'FACE'")

    def select_loop(self, edge_index):
        """
        [EDIT MODE][SELECTION-BASED][SAFE] Selects an edge loop based on the target edge index.
        """
        obj, previous_mode = self._ensure_edit_mode()
        
        bm = bmesh.from_edit_mesh(obj.data)
        
        # Validate edge index
        if edge_index < 0 or edge_index >= len(bm.edges):
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError(f"Invalid edge_index {edge_index}. Mesh has {len(bm.edges)} edges (0-{len(bm.edges)-1})")
        
        # Deselect all first
        for edge in bm.edges:
            edge.select = False
        for vert in bm.verts:
            vert.select = False
        for face in bm.faces:
            face.select = False
        
        # Select the target edge
        target_edge = bm.edges[edge_index]
        target_edge.select = True
        
        # Ensure mesh is updated
        bmesh.update_edit_mesh(obj.data)
        
        # Use Blender's loop selection operator
        bpy.ops.mesh.loop_multi_select(ring=False)
        
        # Restore previous mode
        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)
        
        return f"Selected edge loop from edge {edge_index}"

    def select_ring(self, edge_index):
        """
        [EDIT MODE][SELECTION-BASED][SAFE] Selects an edge ring based on the target edge index.
        """
        obj, previous_mode = self._ensure_edit_mode()
        
        bm = bmesh.from_edit_mesh(obj.data)
        
        # Validate edge index
        if edge_index < 0 or edge_index >= len(bm.edges):
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError(f"Invalid edge_index {edge_index}. Mesh has {len(bm.edges)} edges (0-{len(bm.edges)-1})")
        
        # Deselect all first
        for edge in bm.edges:
            edge.select = False
        for vert in bm.verts:
            vert.select = False
        for face in bm.faces:
            face.select = False
        
        # Select the target edge
        target_edge = bm.edges[edge_index]
        target_edge.select = True
        
        # Ensure mesh is updated
        bmesh.update_edit_mesh(obj.data)
        
        # Use Blender's ring selection operator
        bpy.ops.mesh.loop_multi_select(ring=True)
        
        # Restore previous mode
        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)
        
        return f"Selected edge ring from edge {edge_index}"

    def select_linked(self):
        """
        [EDIT MODE][SELECTION-BASED][SAFE] Selects all geometry linked to current selection.
        """
        obj, previous_mode = self._ensure_edit_mode()
        
        bm = bmesh.from_edit_mesh(obj.data)
        
        # Check if anything is selected
        selected_count = sum(1 for v in bm.verts if v.select)
        
        if selected_count == 0:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError("No geometry selected. Select at least one vertex/edge/face to use select_linked")
        
        # Use Blender's select_linked operator
        bpy.ops.mesh.select_linked()
        
        # Count selected after operation
        final_count = sum(1 for v in bm.verts if v.select)
        
        # Restore previous mode
        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)
        
        return f"Selected linked geometry ({final_count} vertices total)"
