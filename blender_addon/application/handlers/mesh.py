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

    def select(self, action="all", boundary_mode="EDGE"):
        """
        [EDIT MODE][SELECTION-BASED][SAFE] Selection helper for basic actions.

        Args:
            action: all, none, linked, more, less, boundary
            boundary_mode: EDGE or VERT (only for boundary action)
        """
        if action == "all":
            return self.select_all(deselect=False)
        if action == "none":
            return self.select_all(deselect=True)
        if action == "linked":
            return self.select_linked()
        if action == "more":
            return self.select_more()
        if action == "less":
            return self.select_less()
        if action == "boundary":
            return self.select_boundary(mode=boundary_mode)
        raise ValueError(f"Unknown selection action: {action}")

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
        # Ensure edit mode before any mesh operations
        self._ensure_edit_mode()

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

    def select_more(self):
        """
        [EDIT MODE][SELECTION-BASED][SAFE] Grows the current selection by one step.
        """
        obj, previous_mode = self._ensure_edit_mode()
        
        bm = bmesh.from_edit_mesh(obj.data)
        
        # Count selected before
        initial_count = sum(1 for v in bm.verts if v.select)
        
        if initial_count == 0:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError("No geometry selected. Select at least one element to grow selection")
        
        # Grow selection
        bpy.ops.mesh.select_more()
        
        # Count selected after
        final_count = sum(1 for v in bm.verts if v.select)
        
        # Restore previous mode
        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)
        
        return f"Grew selection by one step ({initial_count} -> {final_count} vertices)"

    def select_less(self):
        """
        [EDIT MODE][SELECTION-BASED][SAFE] Shrinks the current selection by one step.
        """
        obj, previous_mode = self._ensure_edit_mode()
        
        bm = bmesh.from_edit_mesh(obj.data)
        
        # Count selected before
        initial_count = sum(1 for v in bm.verts if v.select)
        
        if initial_count == 0:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError("No geometry selected. Select at least one element to shrink selection")
        
        # Shrink selection
        bpy.ops.mesh.select_less()
        
        # Count selected after
        final_count = sum(1 for v in bm.verts if v.select)
        
        # Restore previous mode
        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)
        
        return f"Shrunk selection by one step ({initial_count} -> {final_count} vertices)"

    def get_vertex_data(self, object_name, selected_only=False):
        """
        [EDIT MODE][READ-ONLY][SAFE] Returns vertex positions and selection states.
        """
        obj = bpy.data.objects.get(object_name)
        if not obj:
            raise ValueError(f"Object '{object_name}' not found")
        if obj.type != 'MESH':
            raise ValueError(f"Object '{object_name}' is not a MESH (type: {obj.type})")
        
        # Ensure we're in EDIT mode to read bmesh data
        prev_mode = obj.mode
        bpy.context.view_layer.objects.active = obj
        if prev_mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
        
        bm = bmesh.from_edit_mesh(obj.data)
        
        vertices = []
        selected_count = 0
        
        for v in bm.verts:
            if v.select:
                selected_count += 1
            
            # Skip if selected_only is True and vertex is not selected
            if selected_only and not v.select:
                continue
            
            vertices.append({
                "index": v.index,
                "position": [round(v.co.x, 6), round(v.co.y, 6), round(v.co.z, 6)],
                "selected": v.select
            })
        
        # Restore previous mode
        if prev_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=prev_mode)
        
        return {
            "object_name": object_name,
            "vertex_count": len(bm.verts),
            "selected_count": selected_count,
            "returned_count": len(vertices),
            "vertices": vertices
        }

    def get_edge_data(self, object_name, selected_only=False):
        """
        [EDIT MODE][READ-ONLY][SAFE] Returns edge connectivity and attributes.
        """
        obj = bpy.data.objects.get(object_name)
        if not obj:
            raise ValueError(f"Object '{object_name}' not found")
        if obj.type != 'MESH':
            raise ValueError(f"Object '{object_name}' is not a MESH (type: {obj.type})")

        prev_mode = obj.mode
        bpy.context.view_layer.objects.active = obj
        if prev_mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')

        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()

        edges = []
        selected_count = 0

        for e in bm.edges:
            if e.select:
                selected_count += 1
            if selected_only and not e.select:
                continue

            smooth = getattr(e, "smooth", True)
            edges.append({
                "index": e.index,
                "verts": [e.verts[0].index, e.verts[1].index],
                "is_boundary": e.is_boundary,
                "is_manifold": e.is_manifold,
                "is_seam": e.seam,
                "is_sharp": not smooth,
                "crease": round(float(getattr(e, "crease", 0.0)), 6),
                "bevel_weight": round(float(getattr(e, "bevel_weight", 0.0)), 6),
                "selected": e.select,
            })

        if prev_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=prev_mode)

        return {
            "object_name": object_name,
            "edge_count": len(bm.edges),
            "selected_count": selected_count,
            "returned_count": len(edges),
            "edges": edges,
        }

    def get_face_data(self, object_name, selected_only=False):
        """
        [EDIT MODE][READ-ONLY][SAFE] Returns face connectivity and attributes.
        """
        obj = bpy.data.objects.get(object_name)
        if not obj:
            raise ValueError(f"Object '{object_name}' not found")
        if obj.type != 'MESH':
            raise ValueError(f"Object '{object_name}' is not a MESH (type: {obj.type})")

        prev_mode = obj.mode
        bpy.context.view_layer.objects.active = obj
        if prev_mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')

        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        faces = []
        selected_count = 0

        for f in bm.faces:
            if f.select:
                selected_count += 1
            if selected_only and not f.select:
                continue

            normal = f.normal
            center = f.calc_center_median()

            faces.append({
                "index": f.index,
                "verts": [v.index for v in f.verts],
                "normal": [round(normal.x, 6), round(normal.y, 6), round(normal.z, 6)],
                "center": [round(center.x, 6), round(center.y, 6), round(center.z, 6)],
                "area": round(float(f.calc_area()), 6),
                "material_index": f.material_index,
                "selected": f.select,
            })

        if prev_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=prev_mode)

        return {
            "object_name": object_name,
            "face_count": len(bm.faces),
            "selected_count": selected_count,
            "returned_count": len(faces),
            "faces": faces,
        }

    def get_uv_data(self, object_name, uv_layer=None, selected_only=False):
        """
        [EDIT MODE][READ-ONLY][SAFE] Returns UVs per face loop.
        """
        obj = bpy.data.objects.get(object_name)
        if not obj:
            raise ValueError(f"Object '{object_name}' not found")
        if obj.type != 'MESH':
            raise ValueError(f"Object '{object_name}' is not a MESH (type: {obj.type})")

        prev_mode = obj.mode
        bpy.context.view_layer.objects.active = obj
        if prev_mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')

        bm = bmesh.from_edit_mesh(obj.data)
        bm.faces.ensure_lookup_table()
        bm.verts.ensure_lookup_table()

        uv_layers = bm.loops.layers.uv
        uv_layer_ref = uv_layers.get(uv_layer) if uv_layer else uv_layers.active
        if uv_layer_ref is None:
            if prev_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=prev_mode)
            if uv_layer:
                raise ValueError(f"UV layer '{uv_layer}' not found")
            raise ValueError(f"Object '{object_name}' has no UV layers")

        faces = []
        selected_count = 0

        for f in bm.faces:
            if f.select:
                selected_count += 1
            if selected_only and not f.select:
                continue

            verts = []
            uvs = []
            for loop in f.loops:
                verts.append(loop.vert.index)
                uv = loop[uv_layer_ref].uv
                uvs.append([round(uv.x, 6), round(uv.y, 6)])

            faces.append({
                "face_index": f.index,
                "verts": verts,
                "uvs": uvs,
            })

        if prev_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=prev_mode)

        return {
            "object_name": object_name,
            "uv_layer": getattr(uv_layer_ref, "name", uv_layer),
            "face_count": len(bm.faces),
            "selected_count": selected_count,
            "returned_count": len(faces),
            "faces": faces,
        }

    def get_loop_normals(self, object_name, selected_only=False):
        """
        [EDIT MODE][READ-ONLY][SAFE] Returns per-loop normals (split/custom).
        """
        obj = bpy.data.objects.get(object_name)
        if not obj:
            raise ValueError(f"Object '{object_name}' not found")
        if obj.type != 'MESH':
            raise ValueError(f"Object '{object_name}' is not a MESH (type: {obj.type})")

        prev_mode = obj.mode
        bpy.context.view_layer.objects.active = obj
        if prev_mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')

        bm = bmesh.from_edit_mesh(obj.data)
        bm.faces.ensure_lookup_table()

        selected_faces = set()
        for f in bm.faces:
            if f.select:
                selected_faces.add(f.index)

        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)
        mesh = obj.data
        mesh.calc_normals_split()

        selected_loop_indices = set()
        if selected_faces:
            for poly in mesh.polygons:
                if poly.index in selected_faces:
                    start = poly.loop_start
                    end = start + poly.loop_total
                    for loop_index in range(start, end):
                        selected_loop_indices.add(loop_index)

        loops = []
        for loop_index, loop in enumerate(mesh.loops):
            if selected_only and loop_index not in selected_loop_indices:
                continue
            normal = loop.normal
            loops.append({
                "loop_index": loop_index,
                "vert": loop.vertex_index,
                "normal": [round(normal.x, 6), round(normal.y, 6), round(normal.z, 6)],
            })

        if hasattr(mesh, "free_normals_split"):
            mesh.free_normals_split()

        if prev_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=prev_mode)

        return {
            "object_name": object_name,
            "loop_count": len(mesh.loops),
            "selected_count": len(selected_loop_indices),
            "returned_count": len(loops),
            "loops": loops,
            "auto_smooth": bool(mesh.use_auto_smooth),
            "custom_normals": bool(mesh.has_custom_normals),
        }

    def get_vertex_group_weights(self, object_name, group_name=None, selected_only=False):
        """
        [EDIT MODE][READ-ONLY][SAFE] Returns vertex group weights.
        """
        obj = bpy.data.objects.get(object_name)
        if not obj:
            raise ValueError(f"Object '{object_name}' not found")
        if obj.type != 'MESH':
            raise ValueError(f"Object '{object_name}' is not a MESH (type: {obj.type})")

        prev_mode = obj.mode
        bpy.context.view_layer.objects.active = obj
        if prev_mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')

        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()

        selected_vertices = {v.index for v in bm.verts if v.select}
        selected_count = len(selected_vertices)

        if prev_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=prev_mode)

        if group_name:
            target_group = obj.vertex_groups.get(group_name)
            if not target_group:
                raise ValueError(f"Vertex group '{group_name}' not found")
            groups = [target_group]
        else:
            groups = list(obj.vertex_groups)

        weights_by_group = {vg.index: [] for vg in groups}

        for v in obj.data.vertices:
            if selected_only and v.index not in selected_vertices:
                continue
            for g in v.groups:
                if g.group in weights_by_group:
                    weights_by_group[g.group].append({
                        "vert": v.index,
                        "weight": round(float(g.weight), 6),
                    })

        if group_name:
            weights = weights_by_group[target_group.index]
            return {
                "object_name": object_name,
                "group_name": target_group.name,
                "group_index": target_group.index,
                "selected_count": selected_count,
                "returned_count": len(weights),
                "weights": weights,
            }

        groups_data = []
        for vg in groups:
            weights = weights_by_group[vg.index]
            groups_data.append({
                "name": vg.name,
                "index": vg.index,
                "weight_count": len(weights),
                "weights": weights,
            })

        return {
            "object_name": object_name,
            "group_count": len(groups_data),
            "selected_count": selected_count,
            "groups": groups_data,
        }

    def get_attributes(self, object_name, attribute_name=None, selected_only=False):
        """
        [EDIT MODE][READ-ONLY][SAFE] Returns mesh attribute data.
        """
        obj = bpy.data.objects.get(object_name)
        if not obj:
            raise ValueError(f"Object '{object_name}' not found")
        if obj.type != 'MESH':
            raise ValueError(f"Object '{object_name}' is not a MESH (type: {obj.type})")

        prev_mode = obj.mode
        bpy.context.view_layer.objects.active = obj
        if prev_mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')

        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        selected_verts = {v.index for v in bm.verts if v.select}
        selected_edges = {e.index for e in bm.edges if e.select}
        selected_faces = {f.index for f in bm.faces if f.select}

        if prev_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=prev_mode)

        mesh = obj.data
        attributes = mesh.attributes

        if attribute_name is None:
            attrs_data = []
            for attr in attributes:
                attrs_data.append({
                    "name": attr.name,
                    "data_type": attr.data_type,
                    "domain": attr.domain,
                })
            return {
                "object_name": object_name,
                "attribute_count": len(attrs_data),
                "attributes": attrs_data,
            }

        attr = attributes.get(attribute_name)
        if attr is None:
            raise ValueError(f"Attribute '{attribute_name}' not found")

        def _coerce_value(value):
            if isinstance(value, bool):
                return bool(value)
            if isinstance(value, int):
                return int(value)
            try:
                return round(float(value), 6)
            except (TypeError, ValueError):
                return value

        def _coerce_sequence(seq):
            values = []
            try:
                values = list(seq)
            except TypeError:
                for attr_name in ("x", "y", "z", "w"):
                    if hasattr(seq, attr_name):
                        values.append(getattr(seq, attr_name))
            return [_coerce_value(value) for value in values]

        selected_indices = None
        selected_count = 0
        domain = attr.domain

        if domain == 'POINT':
            selected_indices = selected_verts
            selected_count = len(selected_verts)
        elif domain == 'EDGE':
            selected_indices = selected_edges
            selected_count = len(selected_edges)
        elif domain == 'FACE':
            selected_indices = selected_faces
            selected_count = len(selected_faces)
        elif domain == 'CORNER':
            selected_loop_indices = set()
            if selected_faces:
                for poly in mesh.polygons:
                    if poly.index in selected_faces:
                        start = poly.loop_start
                        end = start + poly.loop_total
                        for loop_index in range(start, end):
                            selected_loop_indices.add(loop_index)
            selected_indices = selected_loop_indices
            selected_count = len(selected_loop_indices)

        values = []
        data_type = attr.data_type
        for index, data in enumerate(attr.data):
            if selected_only and selected_indices is not None and index not in selected_indices:
                continue

            if data_type in ("FLOAT_COLOR", "BYTE_COLOR"):
                value = _coerce_sequence(getattr(data, "color", []))
            elif data_type in ("FLOAT_VECTOR", "FLOAT2"):
                value = _coerce_sequence(getattr(data, "vector", []))
            elif hasattr(data, "value"):
                value = _coerce_value(data.value)
            elif hasattr(data, "vector"):
                value = _coerce_sequence(data.vector)
            elif hasattr(data, "color"):
                value = _coerce_sequence(data.color)
            else:
                value = None

            values.append({
                "index": index,
                "value": value,
            })

        return {
            "object_name": object_name,
            "attribute": {
                "name": attr.name,
                "data_type": attr.data_type,
                "domain": attr.domain,
            },
            "element_count": len(attr.data),
            "selected_count": selected_count,
            "returned_count": len(values),
            "values": values,
        }

    def get_shape_keys(self, object_name, include_deltas=False):
        """
        [OBJECT MODE][READ-ONLY][SAFE] Returns shape key data.
        """
        obj = bpy.data.objects.get(object_name)
        if not obj:
            raise ValueError(f"Object '{object_name}' not found")
        if obj.type != 'MESH':
            raise ValueError(f"Object '{object_name}' is not a MESH (type: {obj.type})")

        prev_mode = obj.mode
        bpy.context.view_layer.objects.active = obj
        if prev_mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        shape_keys = obj.data.shape_keys
        if not shape_keys or not shape_keys.key_blocks:
            if prev_mode != 'OBJECT':
                bpy.ops.object.mode_set(mode=prev_mode)
            return {
                "object_name": object_name,
                "shape_key_count": 0,
                "shape_keys": [],
            }

        key_blocks = shape_keys.key_blocks
        basis = key_blocks[0]
        shape_keys_data = []
        threshold = 1e-6

        for block in key_blocks:
            entry = {
                "name": block.name,
                "value": round(float(block.value), 6),
            }

            if include_deltas:
                deltas = []
                if block != basis:
                    for index, key_point in enumerate(block.data):
                        basis_point = basis.data[index]
                        dx = key_point.co.x - basis_point.co.x
                        dy = key_point.co.y - basis_point.co.y
                        dz = key_point.co.z - basis_point.co.z
                        if abs(dx) > threshold or abs(dy) > threshold or abs(dz) > threshold:
                            deltas.append({
                                "vert": index,
                                "delta": [
                                    round(dx, 6),
                                    round(dy, 6),
                                    round(dz, 6),
                                ],
                            })
                entry["deltas"] = deltas

            shape_keys_data.append(entry)

        if prev_mode != 'OBJECT':
            bpy.ops.object.mode_set(mode=prev_mode)

        return {
            "object_name": object_name,
            "shape_key_count": len(key_blocks),
            "shape_keys": shape_keys_data,
        }

    def select_by_location(self, axis, min_coord, max_coord, mode='VERT'):
        """
        [EDIT MODE][SELECTION-BASED][SAFE] Selects geometry within coordinate range.
        """
        obj, previous_mode = self._ensure_edit_mode()
        
        bm = bmesh.from_edit_mesh(obj.data)
        
        # Validate axis
        axis = axis.upper()
        if axis not in ['X', 'Y', 'Z']:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError(f"Invalid axis '{axis}'. Must be X, Y, or Z")
        
        # Validate mode
        mode = mode.upper()
        if mode not in ['VERT', 'EDGE', 'FACE']:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError(f"Invalid mode '{mode}'. Must be VERT, EDGE, or FACE")
        
        axis_idx = {'X': 0, 'Y': 1, 'Z': 2}[axis]
        selected_count = 0
        
        # Deselect all first
        for v in bm.verts:
            v.select = False
        for e in bm.edges:
            e.select = False
        for f in bm.faces:
            f.select = False
        
        if mode == 'VERT':
            for v in bm.verts:
                coord = v.co[axis_idx]
                if min_coord <= coord <= max_coord:
                    v.select = True
                    selected_count += 1
        
        elif mode == 'EDGE':
            for e in bm.edges:
                # Check if both verts are in range
                v1_coord = e.verts[0].co[axis_idx]
                v2_coord = e.verts[1].co[axis_idx]
                avg_coord = (v1_coord + v2_coord) / 2
                if min_coord <= avg_coord <= max_coord:
                    e.select = True
                    e.verts[0].select = True
                    e.verts[1].select = True
                    selected_count += 1
        
        elif mode == 'FACE':
            for f in bm.faces:
                # Use face centroid
                centroid = f.calc_center_median()
                coord = centroid[axis_idx]
                if min_coord <= coord <= max_coord:
                    f.select = True
                    for v in f.verts:
                        v.select = True
                    for e in f.edges:
                        e.select = True
                    selected_count += 1
        
        bmesh.update_edit_mesh(obj.data)
        
        # Restore previous mode
        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)
        
        return f"Selected {selected_count} {mode.lower()}(s) in range {axis}=[{min_coord}, {max_coord}]"

    def select_boundary(self, mode='EDGE'):
        """
        [EDIT MODE][SELECTION-BASED][SAFE] Selects boundary edges or vertices.
        """
        obj, previous_mode = self._ensure_edit_mode()

        bm = bmesh.from_edit_mesh(obj.data)

        # Validate mode
        mode = mode.upper()
        if mode not in ['EDGE', 'VERT']:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError(f"Invalid mode '{mode}'. Must be EDGE or VERT")

        # Deselect all first
        for v in bm.verts:
            v.select = False
        for e in bm.edges:
            e.select = False
        for f in bm.faces:
            f.select = False

        selected_count = 0

        if mode == 'EDGE':
            # Select boundary edges (edges with only 1 adjacent face)
            for edge in bm.edges:
                if edge.is_boundary:
                    edge.select = True
                    edge.verts[0].select = True
                    edge.verts[1].select = True
                    selected_count += 1

        elif mode == 'VERT':
            # Select boundary vertices
            for vert in bm.verts:
                if vert.is_boundary:
                    vert.select = True
                    selected_count += 1

        bmesh.update_edit_mesh(obj.data)

        # Restore previous mode
        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)

        return f"Selected {selected_count} boundary {mode.lower()}(s)"

    # ==========================================================================
    # TASK-016: Organic & Deform Tools
    # ==========================================================================

    def randomize(self, amount=0.1, uniform=0.0, normal=0.0, seed=0):
        """
        [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Randomizes vertex positions.
        Uses bpy.ops.transform.vertex_random for displacement.
        """
        obj, previous_mode = self._ensure_edit_mode()

        bm = bmesh.from_edit_mesh(obj.data)
        selected_count = sum(1 for v in bm.verts if v.select)

        if selected_count == 0:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError("No vertices selected")

        # bpy.ops.transform.vertex_random parameters:
        # offset: maximum displacement
        # uniform: uniform random factor (0-1)
        # normal: normal-based factor (0-1)
        # seed: random seed
        bpy.ops.transform.vertex_random(
            offset=amount,
            uniform=uniform,
            normal=normal,
            seed=seed
        )

        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)

        return f"Randomized {selected_count} vertices (amount={amount}, uniform={uniform}, normal={normal}, seed={seed})"

    def shrink_fatten(self, value):
        """
        [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Moves vertices along their normals.
        Positive values = fatten (outward), negative values = shrink (inward).
        """
        obj, previous_mode = self._ensure_edit_mode()

        bm = bmesh.from_edit_mesh(obj.data)
        selected_count = sum(1 for v in bm.verts if v.select)

        if selected_count == 0:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError("No vertices selected")

        # bpy.ops.transform.shrink_fatten moves selection along normals
        bpy.ops.transform.shrink_fatten(value=value)

        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)

        direction = "fattened" if value > 0 else "shrunk"
        return f"Shrink/Fatten: {direction} {selected_count} vertices by {abs(value)}"

    # ==========================================================================
    # TASK-017: Vertex Group Tools
    # ==========================================================================

    def create_vertex_group(self, object_name, name):
        """
        [MESH][SAFE] Creates a new vertex group on the specified mesh object.
        """
        if object_name not in bpy.data.objects:
            raise ValueError(f"Object '{object_name}' not found")

        obj = bpy.data.objects[object_name]

        if obj.type != 'MESH':
            raise ValueError(f"Object '{object_name}' is not a MESH (type: {obj.type})")

        # Check if group already exists
        if name in obj.vertex_groups:
            raise ValueError(f"Vertex group '{name}' already exists on '{object_name}'")

        # Create new vertex group
        vg = obj.vertex_groups.new(name=name)

        return f"Created vertex group '{vg.name}' on '{object_name}' (index: {vg.index})"

    def assign_to_group(self, object_name, group_name, weight=1.0):
        """
        [EDIT MODE][SELECTION-BASED][SAFE] Assigns selected vertices to a vertex group.
        """
        if object_name not in bpy.data.objects:
            raise ValueError(f"Object '{object_name}' not found")

        obj = bpy.data.objects[object_name]

        if obj.type != 'MESH':
            raise ValueError(f"Object '{object_name}' is not a MESH (type: {obj.type})")

        if group_name not in obj.vertex_groups:
            raise ValueError(f"Vertex group '{group_name}' not found on '{object_name}'")

        # Validate weight
        weight = max(0.0, min(1.0, weight))

        # Ensure we're in EDIT mode and object is active
        bpy.context.view_layer.objects.active = obj
        prev_mode = obj.mode
        if prev_mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')

        bm = bmesh.from_edit_mesh(obj.data)
        selected_indices = [v.index for v in bm.verts if v.select]

        if not selected_indices:
            if prev_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=prev_mode)
            raise ValueError("No vertices selected")

        # Set active vertex group
        obj.vertex_groups.active = obj.vertex_groups[group_name]

        # Use operator to assign (works in edit mode)
        bpy.ops.object.vertex_group_assign()

        # If we need to set specific weight, we need to go through the vertices
        # The operator assigns with weight based on weight paint tools
        # For specific weight, we use the vertex group API directly
        if weight != 1.0:
            # Need to briefly switch to object mode to modify weights
            bpy.ops.object.mode_set(mode='OBJECT')
            vg = obj.vertex_groups[group_name]
            vg.add(selected_indices, weight, 'REPLACE')
            bpy.ops.object.mode_set(mode='EDIT')

        # Restore previous mode
        if prev_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=prev_mode)

        return f"Assigned {len(selected_indices)} vertices to '{group_name}' with weight {weight}"

    def remove_from_group(self, object_name, group_name):
        """
        [EDIT MODE][SELECTION-BASED][SAFE] Removes selected vertices from a vertex group.
        """
        if object_name not in bpy.data.objects:
            raise ValueError(f"Object '{object_name}' not found")

        obj = bpy.data.objects[object_name]

        if obj.type != 'MESH':
            raise ValueError(f"Object '{object_name}' is not a MESH (type: {obj.type})")

        if group_name not in obj.vertex_groups:
            raise ValueError(f"Vertex group '{group_name}' not found on '{object_name}'")

        # Ensure we're in EDIT mode and object is active
        bpy.context.view_layer.objects.active = obj
        prev_mode = obj.mode
        if prev_mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')

        bm = bmesh.from_edit_mesh(obj.data)
        selected_indices = [v.index for v in bm.verts if v.select]

        if not selected_indices:
            if prev_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=prev_mode)
            raise ValueError("No vertices selected")

        # Set active vertex group
        obj.vertex_groups.active = obj.vertex_groups[group_name]

        # Use operator to remove (works in edit mode)
        bpy.ops.object.vertex_group_remove_from()

        # Restore previous mode
        if prev_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=prev_mode)

        return f"Removed {len(selected_indices)} vertices from '{group_name}'"

    # ==========================================================================
    # TASK-018: Phase 2.5 - Advanced Precision Tools
    # ==========================================================================

    def bisect(self, plane_co, plane_no, clear_inner=False, clear_outer=False, fill=False):
        """
        [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Cuts mesh along a plane.
        Uses bpy.ops.mesh.bisect.
        """
        obj, previous_mode = self._ensure_edit_mode()

        bm = bmesh.from_edit_mesh(obj.data)
        selected_count = sum(1 for v in bm.verts if v.select)

        if selected_count == 0:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError("No geometry selected. Select geometry to bisect.")

        # Validate inputs
        if len(plane_co) != 3:
            raise ValueError(f"plane_co must be [x, y, z], got {plane_co}")
        if len(plane_no) != 3:
            raise ValueError(f"plane_no must be [x, y, z], got {plane_no}")

        # Execute bisect
        bpy.ops.mesh.bisect(
            plane_co=tuple(plane_co),
            plane_no=tuple(plane_no),
            clear_inner=clear_inner,
            clear_outer=clear_outer,
            use_fill=fill
        )

        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)

        options = []
        if clear_inner:
            options.append("cleared inner")
        if clear_outer:
            options.append("cleared outer")
        if fill:
            options.append("filled")
        options_str = f" ({', '.join(options)})" if options else ""

        return f"Bisected mesh at plane_co={plane_co}, plane_no={plane_no}{options_str}"

    def edge_slide(self, value=0.0):
        """
        [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Slides selected edges along topology.
        Uses bpy.ops.transform.edge_slide.
        """
        obj, previous_mode = self._ensure_edit_mode()

        bm = bmesh.from_edit_mesh(obj.data)
        selected_edges = sum(1 for e in bm.edges if e.select)

        if selected_edges == 0:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError("No edges selected. Select edges to slide.")

        # Clamp value to valid range
        value = max(-1.0, min(1.0, value))

        bpy.ops.transform.edge_slide(value=value)

        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)

        return f"Slid {selected_edges} edge(s) by {value}"

    def vert_slide(self, value=0.0):
        """
        [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Slides selected vertices along connected edges.
        Uses bpy.ops.transform.vert_slide.
        """
        obj, previous_mode = self._ensure_edit_mode()

        bm = bmesh.from_edit_mesh(obj.data)
        selected_verts = sum(1 for v in bm.verts if v.select)

        if selected_verts == 0:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError("No vertices selected. Select vertices to slide.")

        # Clamp value to valid range
        value = max(-1.0, min(1.0, value))

        bpy.ops.transform.vert_slide(value=value)

        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)

        return f"Slid {selected_verts} vertex/vertices by {value}"

    def triangulate(self):
        """
        [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Converts selected faces to triangles.
        Uses bpy.ops.mesh.quads_convert_to_tris.
        """
        obj, previous_mode = self._ensure_edit_mode()

        bm = bmesh.from_edit_mesh(obj.data)
        selected_faces = sum(1 for f in bm.faces if f.select)

        if selected_faces == 0:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError("No faces selected. Select faces to triangulate.")

        # Count non-triangular faces
        non_tri_count = sum(1 for f in bm.faces if f.select and len(f.verts) > 3)

        bpy.ops.mesh.quads_convert_to_tris()

        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)

        return f"Triangulated {selected_faces} face(s) ({non_tri_count} were non-triangular)"

    def remesh_voxel(self, voxel_size=0.1, adaptivity=0.0):
        """
        [OBJECT MODE][DESTRUCTIVE] Remeshes object using Voxel algorithm.
        Uses bpy.ops.object.voxel_remesh.
        """
        obj = bpy.context.active_object
        if not obj or obj.type != 'MESH':
            raise ValueError("Active object must be a Mesh.")

        # Ensure we're in Object Mode for voxel remesh
        prev_mode = obj.mode
        if prev_mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # Store original face count for comparison
        original_faces = len(obj.data.polygons)

        # Set voxel remesh parameters on the mesh data
        obj.data.remesh_voxel_size = voxel_size
        obj.data.remesh_voxel_adaptivity = adaptivity

        # Execute voxel remesh
        bpy.ops.object.voxel_remesh()

        # Get new face count
        new_faces = len(obj.data.polygons)

        # Restore previous mode if it was EDIT
        if prev_mode == 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')

        return f"Voxel remesh complete (voxel_size={voxel_size}, adaptivity={adaptivity}). Faces: {original_faces} → {new_faces}"

    # ==========================================================================
    # TASK-019: Phase 2.4 - Core Transform & Geometry
    # ==========================================================================

    def transform_selected(self, translate=None, rotate=None, scale=None, pivot='MEDIAN_POINT'):
        """
        [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Transforms selected geometry.
        Uses bpy.ops.transform.* operators.
        """
        obj, previous_mode = self._ensure_edit_mode()

        bm = bmesh.from_edit_mesh(obj.data)
        selected_count = sum(1 for v in bm.verts if v.select)

        if selected_count == 0:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError("No geometry selected")

        # Set pivot point
        original_pivot = bpy.context.scene.tool_settings.transform_pivot_point
        bpy.context.scene.tool_settings.transform_pivot_point = pivot

        operations = []

        try:
            # Apply translation
            if translate:
                bpy.ops.transform.translate(value=tuple(translate))
                operations.append(f"translated by {translate}")

            # Apply rotation (in radians)
            if rotate:
                # Rotate around each axis
                if rotate[0] != 0:
                    bpy.ops.transform.rotate(value=rotate[0], orient_axis='X')
                if rotate[1] != 0:
                    bpy.ops.transform.rotate(value=rotate[1], orient_axis='Y')
                if rotate[2] != 0:
                    bpy.ops.transform.rotate(value=rotate[2], orient_axis='Z')
                operations.append(f"rotated by {rotate} rad")

            # Apply scale
            if scale:
                bpy.ops.transform.resize(value=tuple(scale))
                operations.append(f"scaled by {scale}")

        finally:
            # Restore original pivot point
            bpy.context.scene.tool_settings.transform_pivot_point = original_pivot

        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)

        if not operations:
            return "No transformation applied (all parameters were None)"

        return f"Transformed {selected_count} vertices: {', '.join(operations)} (pivot: {pivot})"

    def bridge_edge_loops(self, number_cuts=0, interpolation='LINEAR', smoothness=0.0, twist=0):
        """
        [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Bridges two edge loops with faces.
        Uses bpy.ops.mesh.bridge_edge_loops.
        """
        obj, previous_mode = self._ensure_edit_mode()

        bm = bmesh.from_edit_mesh(obj.data)
        selected_edges = sum(1 for e in bm.edges if e.select)

        if selected_edges < 2:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError("Select at least two edge loops to bridge")

        # Execute bridge
        bpy.ops.mesh.bridge_edge_loops(
            type=interpolation,
            number_cuts=number_cuts,
            smoothness=smoothness,
            twist_offset=twist
        )

        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)

        return f"Bridged edge loops (cuts={number_cuts}, interpolation={interpolation}, smoothness={smoothness}, twist={twist})"

    def duplicate_selected(self, translate=None):
        """
        [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Duplicates selected geometry.
        Uses bpy.ops.mesh.duplicate_move.
        """
        obj, previous_mode = self._ensure_edit_mode()

        bm = bmesh.from_edit_mesh(obj.data)
        selected_verts = sum(1 for v in bm.verts if v.select)
        selected_edges = sum(1 for e in bm.edges if e.select)
        selected_faces = sum(1 for f in bm.faces if f.select)

        if selected_verts == 0:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError("No geometry selected")

        # Duplicate with optional translation
        if translate:
            bpy.ops.mesh.duplicate_move(
                MESH_OT_duplicate={},
                TRANSFORM_OT_translate={"value": tuple(translate)}
            )
        else:
            bpy.ops.mesh.duplicate()

        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)

        move_str = f", moved by {translate}" if translate else " (in-place)"
        return f"Duplicated {selected_verts} vertices, {selected_edges} edges, {selected_faces} faces{move_str}"

    # ==========================================================================
    # TASK-021: Phase 2.6 - Curves & Procedural (Mesh-based tools)
    # ==========================================================================

    def spin(self, steps=12, angle=6.283185, axis='Z', center=None, dupli=False):
        """
        [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Spins/lathes selected geometry.
        Uses bpy.ops.mesh.spin.
        """
        obj, previous_mode = self._ensure_edit_mode()

        bm = bmesh.from_edit_mesh(obj.data)
        selected_count = sum(1 for v in bm.verts if v.select)

        if selected_count == 0:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError("No geometry selected. Select a profile to spin.")

        # Determine axis vector
        axis_map = {
            'X': (1, 0, 0),
            'Y': (0, 1, 0),
            'Z': (0, 0, 1)
        }
        axis_upper = axis.upper()
        if axis_upper not in axis_map:
            raise ValueError(f"Invalid axis '{axis}'. Must be X, Y, or Z")

        axis_vector = axis_map[axis_upper]

        # Center defaults to 3D cursor if not provided
        if center is None:
            center = list(bpy.context.scene.cursor.location)

        # Execute spin
        bpy.ops.mesh.spin(
            steps=steps,
            angle=angle,
            center=tuple(center),
            axis=axis_vector,
            dupli=dupli
        )

        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)

        degrees = round(angle * 180 / 3.14159, 1)
        dupli_str = " (duplicate mode)" if dupli else ""
        return f"Spin complete: {steps} steps, {degrees}° around {axis} at center {center}{dupli_str}"

    def screw(self, steps=12, turns=1, axis='Z', center=None, offset=0.0):
        """
        [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Creates spiral/screw geometry.
        Uses bpy.ops.mesh.screw.
        """
        obj, previous_mode = self._ensure_edit_mode()

        bm = bmesh.from_edit_mesh(obj.data)
        selected_count = sum(1 for v in bm.verts if v.select)

        if selected_count == 0:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError("No geometry selected. Select a profile to screw.")

        # Determine axis vector
        axis_map = {
            'X': (1, 0, 0),
            'Y': (0, 1, 0),
            'Z': (0, 0, 1)
        }
        axis_upper = axis.upper()
        if axis_upper not in axis_map:
            raise ValueError(f"Invalid axis '{axis}'. Must be X, Y, or Z")

        axis_vector = axis_map[axis_upper]

        # Center defaults to 3D cursor if not provided
        if center is None:
            center = list(bpy.context.scene.cursor.location)

        # Execute screw
        bpy.ops.mesh.screw(
            steps=steps,
            turns=turns,
            center=tuple(center),
            axis=axis_vector,
            screw_offset=offset
        )

        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)

        return f"Screw complete: {steps} steps, {turns} turn(s), offset={offset} around {axis} at center {center}"

    def add_vertex(self, position):
        """
        [EDIT MODE][DESTRUCTIVE] Adds a single vertex at the specified position.
        Uses BMesh API.
        """
        obj, previous_mode = self._ensure_edit_mode()

        if len(position) != 3:
            raise ValueError(f"position must be [x, y, z], got {position}")

        bm = bmesh.from_edit_mesh(obj.data)

        # Deselect all first
        for v in bm.verts:
            v.select = False
        for e in bm.edges:
            e.select = False
        for f in bm.faces:
            f.select = False

        # Create new vertex
        new_vert = bm.verts.new(position)
        new_vert.select = True

        # Update mesh
        bmesh.update_edit_mesh(obj.data)

        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)

        return f"Added vertex at {position} (index: {new_vert.index})"

    def add_edge_face(self):
        """
        [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Creates edge or face from selected vertices.
        Uses bpy.ops.mesh.edge_face_add (same as 'F' key).
        """
        obj, previous_mode = self._ensure_edit_mode()

        bm = bmesh.from_edit_mesh(obj.data)
        selected_verts = sum(1 for v in bm.verts if v.select)

        if selected_verts < 2:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError("Select at least 2 vertices to create edge/face")

        # Execute edge/face add
        bpy.ops.mesh.edge_face_add()

        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)

        if selected_verts == 2:
            return f"Created edge from {selected_verts} vertices"
        else:
            return f"Created face from {selected_verts} vertices"

    # ==========================================================================
    # TASK-029: Edge Weights & Creases (Subdivision Control)
    # ==========================================================================

    def edge_crease(self, crease_value=1.0):
        """
        [EDIT MODE][SELECTION-BASED][NON-DESTRUCTIVE] Sets crease weight on selected edges.
        Crease controls how Subdivision Surface modifier affects edges.
        Uses BMesh API for direct edge crease manipulation.
        """
        obj, previous_mode = self._ensure_edit_mode()

        bm = bmesh.from_edit_mesh(obj.data)

        # First check if any edges are selected (quick count)
        has_selection = any(e.select for e in bm.edges)

        if not has_selection:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError("No edges selected. Select edges to set crease weight.")

        # Clamp crease value to valid range
        crease_value = max(0.0, min(1.0, crease_value))

        # Get or create crease layer FIRST - Blender 4.0+ uses float layers
        # Creating a layer may invalidate edge references, so do this before iterating
        crease_layer = None
        if hasattr(bm.edges.layers, 'crease'):
            # Blender 3.x
            crease_layer = bm.edges.layers.crease.verify()
        else:
            # Blender 4.0+ uses float layer named 'crease_edge'
            crease_layer = bm.edges.layers.float.get('crease_edge')
            if crease_layer is None:
                crease_layer = bm.edges.layers.float.new('crease_edge')

        # NOW collect and set crease on selected edges (after layer is created)
        edge_count = 0
        for edge in bm.edges:
            if edge.select:
                edge[crease_layer] = crease_value
                edge_count += 1

        # Update mesh
        bmesh.update_edit_mesh(obj.data)

        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)

        return f"Set crease weight {crease_value} on {edge_count} edge(s)"

    def bevel_weight(self, weight=1.0):
        """
        [EDIT MODE][SELECTION-BASED][NON-DESTRUCTIVE] Sets bevel weight on selected edges.
        When Bevel modifier uses 'Weight' limit method, only edges with weight > 0 are beveled.
        Uses BMesh API for direct bevel weight manipulation.
        """
        obj, previous_mode = self._ensure_edit_mode()

        bm = bmesh.from_edit_mesh(obj.data)

        # First check if any edges are selected (quick count)
        has_selection = any(e.select for e in bm.edges)

        if not has_selection:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError("No edges selected. Select edges to set bevel weight.")

        # Clamp weight to valid range
        weight = max(0.0, min(1.0, weight))

        # Get or create bevel weight layer FIRST - Blender 4.0+ uses float layers
        # Creating a layer may invalidate edge references, so do this before iterating
        bevel_layer = None
        if hasattr(bm.edges.layers, 'bevel_weight'):
            # Blender 3.x
            bevel_layer = bm.edges.layers.bevel_weight.verify()
        else:
            # Blender 4.0+ uses float layer named 'bevel_weight_edge'
            bevel_layer = bm.edges.layers.float.get('bevel_weight_edge')
            if bevel_layer is None:
                bevel_layer = bm.edges.layers.float.new('bevel_weight_edge')

        # NOW collect and set bevel weight on selected edges (after layer is created)
        edge_count = 0
        for edge in bm.edges:
            if edge.select:
                edge[bevel_layer] = weight
                edge_count += 1

        # Update mesh
        bmesh.update_edit_mesh(obj.data)

        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)

        return f"Set bevel weight {weight} on {edge_count} edge(s)"

    def mark_sharp(self, action="mark"):
        """
        [EDIT MODE][SELECTION-BASED][NON-DESTRUCTIVE] Marks or clears sharp edges.
        Sharp edges affect Auto Smooth, Edge Split modifier, and normal calculations.
        Uses bpy.ops.mesh.mark_sharp.
        """
        obj, previous_mode = self._ensure_edit_mode()

        bm = bmesh.from_edit_mesh(obj.data)

        # Count selected edges
        selected_edges = sum(1 for e in bm.edges if e.select)

        if selected_edges == 0:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError("No edges selected. Select edges to mark/clear sharp.")

        # Validate action
        action = action.lower()
        if action not in ["mark", "clear"]:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError(f"Invalid action '{action}'. Must be 'mark' or 'clear'.")

        # Execute mark_sharp
        if action == "mark":
            bpy.ops.mesh.mark_sharp()
            action_desc = "Marked"
        else:
            bpy.ops.mesh.mark_sharp(clear=True)
            action_desc = "Cleared sharp from"

        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)

        return f"{action_desc} {selected_edges} edge(s) as sharp"

    # TASK-030-1: Mesh Dissolve Tool
    def dissolve(self, dissolve_type="limited", angle_limit=5.0, use_face_split=False, use_boundary_tear=False):
        """
        [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Dissolves selected geometry while preserving shape.

        dissolve_type options:
        - 'limited': Dissolve based on angle limit (planar faces)
        - 'verts': Dissolve selected vertices
        - 'edges': Dissolve selected edges
        - 'faces': Dissolve selected faces
        """
        obj, previous_mode = self._ensure_edit_mode()

        # Validate dissolve_type
        valid_types = ["limited", "verts", "edges", "faces"]
        dissolve_type = dissolve_type.lower()
        if dissolve_type not in valid_types:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError(f"Invalid dissolve_type '{dissolve_type}'. Must be one of: {valid_types}")

        # Convert angle to radians for limited dissolve
        import math
        angle_limit_rad = math.radians(angle_limit)

        try:
            if dissolve_type == "limited":
                bpy.ops.mesh.dissolve_limited(
                    angle_limit=angle_limit_rad,
                    use_dissolve_boundaries=use_boundary_tear
                )
                result_desc = f"Limited dissolve (angle: {angle_limit}°)"
            elif dissolve_type == "verts":
                bpy.ops.mesh.dissolve_verts(
                    use_face_split=use_face_split,
                    use_boundary_tear=use_boundary_tear
                )
                result_desc = "Dissolved selected vertices"
            elif dissolve_type == "edges":
                bpy.ops.mesh.dissolve_edges(
                    use_verts=True,
                    use_face_split=use_face_split
                )
                result_desc = "Dissolved selected edges"
            else:  # faces
                bpy.ops.mesh.dissolve_faces(use_verts=True)
                result_desc = "Dissolved selected faces"
        except RuntimeError as e:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise RuntimeError(f"Dissolve failed: {e}")

        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)

        return f"{result_desc} completed successfully"

    # TASK-030-2: Mesh Tris To Quads Tool
    def tris_to_quads(self, face_threshold=40.0, shape_threshold=40.0):
        """
        [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Converts triangles to quads where possible.

        Merges adjacent triangles into quads based on angle thresholds.
        face_threshold: Maximum angle between face normals (degrees)
        shape_threshold: Maximum shape deviation allowed (degrees)
        """
        obj, previous_mode = self._ensure_edit_mode()

        # Convert thresholds to radians
        import math
        face_threshold_rad = math.radians(face_threshold)
        shape_threshold_rad = math.radians(shape_threshold)

        try:
            bpy.ops.mesh.tris_convert_to_quads(
                face_threshold=face_threshold_rad,
                shape_threshold=shape_threshold_rad
            )
        except RuntimeError as e:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise RuntimeError(f"Tris to quads conversion failed: {e}")

        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)

        return f"Converted triangles to quads (face threshold: {face_threshold}°, shape threshold: {shape_threshold}°)"

    # TASK-030-3: Mesh Normals Make Consistent Tool
    def normals_make_consistent(self, inside=False):
        """
        [EDIT MODE][SELECTION-BASED][NON-DESTRUCTIVE] Recalculates normals to face consistently.

        Makes all normals point in the same direction (outward by default).
        inside: If True, normals point inward instead of outward
        """
        obj, previous_mode = self._ensure_edit_mode()

        try:
            bpy.ops.mesh.normals_make_consistent(inside=inside)
        except RuntimeError as e:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise RuntimeError(f"Normals recalculation failed: {e}")

        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)

        direction = "inward" if inside else "outward"
        return f"Recalculated normals to face consistently {direction}"

    # TASK-030-4: Mesh Decimate Tool
    def decimate(self, ratio=0.5, use_symmetry=False, symmetry_axis="X"):
        """
        [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Reduces polycount while preserving shape.

        Uses collapse decimation to reduce geometry complexity.
        ratio: Target ratio of faces to keep (0.0 to 1.0)
        use_symmetry: Maintain mesh symmetry during decimation
        symmetry_axis: Axis for symmetry ('X', 'Y', or 'Z')
        """
        obj, previous_mode = self._ensure_edit_mode()

        # Validate ratio
        ratio = max(0.0, min(1.0, ratio))

        # Validate symmetry axis
        valid_axes = ['X', 'Y', 'Z']
        symmetry_axis = symmetry_axis.upper()
        if symmetry_axis not in valid_axes:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError(f"Invalid symmetry_axis '{symmetry_axis}'. Must be one of: {valid_axes}")

        try:
            bpy.ops.mesh.decimate(
                ratio=ratio,
                use_symmetry=use_symmetry,
                symmetry_axis=symmetry_axis
            )
        except RuntimeError as e:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise RuntimeError(f"Decimate failed: {e}")

        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)

        symmetry_desc = f" with {symmetry_axis} symmetry" if use_symmetry else ""
        return f"Decimated mesh to {ratio*100:.1f}% of original{symmetry_desc}"

    # ==========================================================================
    # TASK-032: Knife & Cut Tools
    # ==========================================================================

    def knife_project(self, cut_through=True):
        """
        [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Projects cut from selected geometry.

        Projects knife cut from view using selected edges/faces as cutter.
        Requires specific view angle - best used with orthographic views.
        """
        obj, previous_mode = self._ensure_edit_mode()

        bm = bmesh.from_edit_mesh(obj.data)
        selected_count = sum(1 for f in bm.faces if f.select)

        try:
            bpy.ops.mesh.knife_project(cut_through=cut_through)
        except RuntimeError as e:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise RuntimeError(f"Knife project failed: {e}")

        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)

        cut_mode = "through entire mesh" if cut_through else "visible faces only"
        return f"Knife project completed ({cut_mode})"

    def rip(self, use_fill=False):
        """
        [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Rips (tears) geometry at selection.

        Creates a hole/tear at selected vertices. Uses mesh.rip_move operator.
        Note: Rips from the center of selection.
        """
        obj, previous_mode = self._ensure_edit_mode()

        bm = bmesh.from_edit_mesh(obj.data)
        selected_verts = sum(1 for v in bm.verts if v.select)

        if selected_verts == 0:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError("No vertices selected. Select vertices to rip.")

        try:
            # Find 3D View context for operators that require it
            view_area = None
            view_region = None

            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    view_area = area
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            view_region = region
                    break

            if view_area and view_region:
                # Use context override for rip_move
                with bpy.context.temp_override(area=view_area, region=view_region):
                    bpy.ops.mesh.rip_move(
                        MESH_OT_rip={'use_fill': use_fill},
                        TRANSFORM_OT_translate={'value': (0, 0, 0)}
                    )
            else:
                # Fallback: use split as alternative (different behavior but similar result)
                bpy.ops.mesh.split()
                if use_fill:
                    bpy.ops.mesh.edge_face_add()
        except RuntimeError as e:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise RuntimeError(f"Rip failed: {e}")

        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)

        fill_desc = " (hole filled)" if use_fill else ""
        return f"Ripped {selected_verts} vertex(es){fill_desc}"

    def split(self):
        """
        [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Splits selection from mesh.

        Unlike 'separate', split keeps geometry in the same object
        but disconnects it from surrounding geometry.
        """
        obj, previous_mode = self._ensure_edit_mode()

        bm = bmesh.from_edit_mesh(obj.data)
        selected_verts = sum(1 for v in bm.verts if v.select)
        selected_faces = sum(1 for f in bm.faces if f.select)

        if selected_verts == 0:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError("No geometry selected. Select geometry to split.")

        try:
            bpy.ops.mesh.split()
        except RuntimeError as e:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise RuntimeError(f"Split failed: {e}")

        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)

        return f"Split {selected_verts} vertices ({selected_faces} faces) from mesh"

    def edge_split(self):
        """
        [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Splits mesh at selected edges.

        Creates a seam/split along selected edges. Geometry becomes disconnected
        but stays in place (vertices are duplicated at the split).
        """
        obj, previous_mode = self._ensure_edit_mode()

        bm = bmesh.from_edit_mesh(obj.data)
        selected_edges = sum(1 for e in bm.edges if e.select)

        if selected_edges == 0:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError("No edges selected. Select edges to split.")

        try:
            bpy.ops.mesh.edge_split()
        except RuntimeError as e:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise RuntimeError(f"Edge split failed: {e}")

        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)

        return f"Split mesh at {selected_edges} edge(s)"

    # ==========================================================================
    # TASK-038-5: Proportional Editing
    # ==========================================================================

    def set_proportional_edit(
        self,
        enabled: bool = True,
        falloff_type: str = "SMOOTH",
        size: float = 1.0,
        use_connected: bool = False,
    ):
        """
        [EDIT MODE][SETTING] Configures proportional editing mode.

        Proportional editing affects nearby unselected geometry when transforming.
        Essential for organic modeling - creates smooth falloff in deformations.
        """
        # Validate falloff type
        valid_falloffs = [
            "SMOOTH", "SPHERE", "ROOT", "INVERSE_SQUARE",
            "SHARP", "LINEAR", "CONSTANT", "RANDOM"
        ]
        falloff_type = falloff_type.upper()
        if falloff_type not in valid_falloffs:
            raise ValueError(f"Invalid falloff type: {falloff_type}. Valid: {valid_falloffs}")

        # Get tool settings
        tool_settings = bpy.context.tool_settings

        # Set proportional edit mode
        if enabled:
            if use_connected:
                tool_settings.proportional_edit = 'CONNECTED'
            else:
                tool_settings.proportional_edit = 'ENABLED'
        else:
            tool_settings.proportional_edit = 'DISABLED'

        # Set falloff type
        tool_settings.proportional_edit_falloff = falloff_type

        # Set size
        tool_settings.proportional_size = max(0.001, size)

        # Build status message
        if enabled:
            mode = "connected" if use_connected else "enabled"
            return (
                f"Proportional editing {mode} "
                f"(falloff={falloff_type}, size={size})"
            )
        else:
            return "Proportional editing disabled"

    # ==========================================================================
    # TASK-036: Symmetry & Advanced Fill Tools
    # ==========================================================================

    def symmetrize(self, direction="NEGATIVE_X", threshold=0.0001):
        """
        [EDIT MODE][DESTRUCTIVE] Symmetrizes mesh.
        Mirrors geometry from one side to the other, making the mesh perfectly symmetric.
        """
        obj, previous_mode = self._ensure_edit_mode()

        # Validate direction
        valid_directions = [
            "NEGATIVE_X", "POSITIVE_X",
            "NEGATIVE_Y", "POSITIVE_Y",
            "NEGATIVE_Z", "POSITIVE_Z"
        ]
        direction = direction.upper()
        if direction not in valid_directions:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError(f"Invalid direction '{direction}'. Must be one of: {valid_directions}")

        try:
            bpy.ops.mesh.symmetrize(direction=direction, threshold=threshold)
        except RuntimeError as e:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise RuntimeError(f"Symmetrize failed: {e}")

        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)

        return f"Symmetrized mesh (direction={direction}, threshold={threshold})"

    def grid_fill(self, span=1, offset=0, use_interp_simple=False):
        """
        [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Fills boundary with a grid of quads.
        Unlike mesh_fill_holes (which creates triangles), grid_fill creates proper quad grid.
        Requirements: Selection must be a closed edge loop (boundary).
        """
        obj, previous_mode = self._ensure_edit_mode()

        bm = bmesh.from_edit_mesh(obj.data)
        selected_edges = sum(1 for e in bm.edges if e.select)

        if selected_edges < 3:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError("Select at least 3 edges forming a closed boundary to use grid fill.")

        try:
            bpy.ops.mesh.fill_grid(span=span, offset=offset, use_interp_simple=use_interp_simple)
        except RuntimeError as e:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise RuntimeError(f"Grid fill failed: {e}")

        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)

        return f"Grid filled boundary (span={span}, offset={offset})"

    def poke_faces(self, offset=0.0, use_relative_offset=False, center_mode="MEDIAN_WEIGHTED"):
        """
        [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Pokes selected faces.
        Adds a vertex at the center of each selected face and connects to edges,
        creating a fan of triangles.
        """
        obj, previous_mode = self._ensure_edit_mode()

        bm = bmesh.from_edit_mesh(obj.data)
        selected_faces = sum(1 for f in bm.faces if f.select)

        if selected_faces == 0:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError("No faces selected. Select faces to poke.")

        # Validate center_mode
        valid_modes = ["MEDIAN", "MEDIAN_WEIGHTED", "BOUNDS"]
        center_mode = center_mode.upper()
        if center_mode not in valid_modes:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError(f"Invalid center_mode '{center_mode}'. Must be one of: {valid_modes}")

        try:
            bpy.ops.mesh.poke(
                offset=offset,
                use_relative_offset=use_relative_offset,
                center_mode=center_mode
            )
        except RuntimeError as e:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise RuntimeError(f"Poke faces failed: {e}")

        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)

        return f"Poked {selected_faces} face(s) (offset={offset}, center_mode={center_mode})"

    def beautify_fill(self, angle_limit=180.0):
        """
        [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Beautifies face arrangement.
        Rotates triangle edges to create more uniform triangulation.
        Useful after boolean operations, triangulation, or import cleanup.
        """
        import math

        obj, previous_mode = self._ensure_edit_mode()

        bm = bmesh.from_edit_mesh(obj.data)
        selected_faces = sum(1 for f in bm.faces if f.select)

        if selected_faces == 0:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError("No faces selected. Select triangulated faces to beautify.")

        # Convert angle to radians
        angle_limit_rad = math.radians(angle_limit)

        try:
            bpy.ops.mesh.beautify_fill(angle_limit=angle_limit_rad)
        except RuntimeError as e:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise RuntimeError(f"Beautify fill failed: {e}")

        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)

        return f"Beautified {selected_faces} face(s) (angle_limit={angle_limit}°)"

    def mirror(self, axis="X", use_mirror_merge=True, merge_threshold=0.001):
        """
        [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Mirrors selected geometry.
        Unlike symmetrize (which replaces one side), mirror creates a copy.
        For non-destructive mirroring, use modeling_add_modifier(type='MIRROR').
        """
        obj, previous_mode = self._ensure_edit_mode()

        bm = bmesh.from_edit_mesh(obj.data)
        selected_verts = sum(1 for v in bm.verts if v.select)

        if selected_verts == 0:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError("No geometry selected. Select geometry to mirror.")

        # Validate axis
        axis = axis.upper()
        if axis not in ['X', 'Y', 'Z']:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError(f"Invalid axis '{axis}'. Must be X, Y, or Z")

        # Determine constraint axis
        constraint_axis = (axis == 'X', axis == 'Y', axis == 'Z')

        try:
            # Use transform.mirror operator
            bpy.ops.transform.mirror(
                orient_type='GLOBAL',
                constraint_axis=constraint_axis
            )

            # Optionally merge mirrored vertices
            if use_mirror_merge:
                bpy.ops.mesh.remove_doubles(threshold=merge_threshold)
        except RuntimeError as e:
            if previous_mode != 'EDIT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise RuntimeError(f"Mirror failed: {e}")

        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=previous_mode)

        merge_desc = f", merged vertices within {merge_threshold}" if use_mirror_merge else ""
        return f"Mirrored {selected_verts} vertices along {axis} axis{merge_desc}"
