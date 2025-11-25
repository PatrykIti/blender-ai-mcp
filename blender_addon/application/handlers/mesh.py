import bpy
import bmesh

class MeshHandler:
    """Application service for Edit Mode mesh operations."""

    def _ensure_edit_mode(self):
        """Ensures the active object is a Mesh and in Edit Mode."""
        obj = bpy.context.active_object
        if not obj or obj.type != 'MESH':
            raise ValueError("Active object must be a Mesh.")
        
        if bpy.context.mode != 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='EDIT')
        
        return obj

    def _get_bmesh(self):
        """Returns the BMesh of the active object."""
        obj = self._ensure_edit_mode()
        bm = bmesh.from_edit_mesh(obj.data)
        return bm

    def select_all(self, deselect=False):
        """Selects or deselects all geometry."""
        self._ensure_edit_mode()
        action = 'DESELECT' if deselect else 'SELECT'
        bpy.ops.mesh.select_all(action=action)
        return "Deselected all" if deselect else "Selected all"

    def delete_selected(self, type='VERT'):
        """Deletes selected elements. Type: VERT, EDGE, FACE."""
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
        Selects elements by index using BMesh.
        type: 'VERT', 'EDGE', 'FACE'
        selection_mode: 'SET' (default), 'ADD', 'SUBTRACT'
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
        """Extrudes selected region."""
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
        """Fills holes (creates faces) from selected edges."""
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
        """Bevels selected geometry."""
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
        Adds a loop cut. 
        NOTE: Loop cut via API is tricky because it relies on mouse position context.
        We will attempt to use 'mesh.subdivide' as a fallback for simple cuts if nothing is selected,
        OR try to use 'mesh.loop_multi_select' if we can simulate context.
        
        For robust automation, 'loopcut_slide' often fails without UI context.
        
        Strategy V1: Use Subdivide if we just want more geometry.
        Strategy V2: If user specifically wants loop cut behavior, we might need bisect or knife_project.
        
        Let's stick to SUBDIVIDE for now if 'loop_cut' is requested in a generic context, 
        or try bpy.ops.mesh.loopcut_slide with generic overrides if possible.
        
        ACTUALLY: The most reliable "cut" for AI without mouse context is 'subdivide' or 'bisect'.
        However, 'loop_cut' implies ring topology.
        
        Let's try bpy.ops.mesh.loopcut_slide. It typically requires a 'region' and 'edge' context.
        If that fails, we'll fallback to subdivide and warn.
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
        """Insets selected faces."""
        self._ensure_edit_mode()
        bpy.ops.mesh.inset(thickness=thickness, depth=depth)
        return f"Inset applied (thickness={thickness}, depth={depth})"

    def boolean(self, operation='DIFFERENCE', solver='FAST'):
        """
        Performs boolean operation in Edit Mode (intersect_boolean).
        Requires selection of target faces.
        operation: 'INTERSECT', 'UNION', 'DIFFERENCE'
        """
        self._ensure_edit_mode()
        bpy.ops.mesh.intersect_boolean(operation=operation, solver=solver)
        return f"Boolean {operation} applied"

    def merge_by_distance(self, distance=0.001):
        """Removes doubles (merges vertices by distance)."""
        self._ensure_edit_mode()
        # Assumes we want to clean up whole selection or everything?
        # Usually 'remove doubles' implies everything selected.
        # Let's rely on current selection.
        bpy.ops.mesh.remove_doubles(threshold=distance)
        return f"Merged vertices by distance {distance}"

    def subdivide(self, number_cuts=1, smoothness=0.0):
        """Subdivides selected geometry."""
        self._ensure_edit_mode()
        bpy.ops.mesh.subdivide(number_cuts=number_cuts, smoothness=smoothness)
        return f"Subdivided selected geometry (cuts={number_cuts})"
