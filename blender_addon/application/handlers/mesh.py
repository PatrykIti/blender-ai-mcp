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
