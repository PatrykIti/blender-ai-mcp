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
        self._ensure_edit_mode()
        # bpy.ops.mesh.delete uses types like 'VERT', 'EDGE', 'FACE'
        bpy.ops.mesh.delete(type=type)
        return f"Deleted selected {type}"

    def select_by_index(self, indices, type='VERT', deselect=False):
        """
        Selects elements by index using BMesh.
        type: 'VERT', 'EDGE', 'FACE'
        """
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
        for i in indices:
            if 0 <= i < len(target_seq):
                # Set select state
                target_seq[i].select = not deselect
                count += 1
        
        # Flush selection to ensure consistent state (e.g. selecting all edges of a face selects the face)
        # But usually for direct selection we just set the flag.
        # Trigger viewport update
        bmesh.update_edit_mesh(bpy.context.active_object.data)
        
        action = "Deselected" if deselect else "Selected"
        return f"{action} {count} {type}(s)"
