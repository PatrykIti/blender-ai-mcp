import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock blender modules
if 'bpy' not in sys.modules:
    sys.modules['bpy'] = MagicMock()
if 'bmesh' not in sys.modules:
    sys.modules['bmesh'] = MagicMock()
    
import bpy
import bmesh

from blender_addon.application.handlers.mesh import MeshHandler

class TestMeshFoundation(unittest.TestCase):
    def setUp(self):
        self.handler = MeshHandler()
        
        # Reset mocks
        bpy.context.active_object = MagicMock()
        bpy.context.active_object.type = 'MESH'
        bpy.context.mode = 'OBJECT'
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.mesh.select_all = MagicMock()
        bpy.ops.mesh.delete = MagicMock()
        bmesh.from_edit_mesh = MagicMock()
        bmesh.update_edit_mesh = MagicMock()

    def test_ensure_edit_mode(self):
        # Setup: Object is in OBJECT mode
        bpy.context.mode = 'OBJECT'
        
        # Execute
        self.handler._ensure_edit_mode()
        
        # Verify mode switch
        bpy.ops.object.mode_set.assert_called_with(mode='EDIT')

    def test_select_all(self):
        # Execute
        self.handler.select_all(deselect=True)
        
        # Verify
        bpy.ops.object.mode_set.assert_called_with(mode='EDIT')
        bpy.ops.mesh.select_all.assert_called_with(action='DESELECT')

    def test_delete_selected(self):
        # Execute
        self.handler.delete_selected(type='FACE')
        
        # Verify
        bpy.ops.object.mode_set.assert_called_with(mode='EDIT')
        bpy.ops.mesh.delete.assert_called_with(type='FACE')

    def test_select_by_index(self):
        # Setup BMesh mock structure
        bm = MagicMock()
        
        # bm.verts must act as a sequence AND have methods like ensure_lookup_table
        mock_verts_seq = MagicMock()
        
        # Create mock items
        v0 = MagicMock(); v0.select = False
        v1 = MagicMock(); v1.select = False
        items = [v0, v1]
        
        # Configure __getitem__ and __len__ to behave like list
        mock_verts_seq.__getitem__.side_effect = items.__getitem__
        mock_verts_seq.__len__.side_effect = items.__len__
        
        bm.verts = mock_verts_seq
        bm.edges = MagicMock()
        bm.faces = MagicMock()
        
        bmesh.from_edit_mesh.return_value = bm
        
        # Execute: Select vertex at index 1
        self.handler.select_by_index(indices=[1], type='VERT', deselect=False)
        
        # Verify
        bmesh.from_edit_mesh.assert_called()
        self.assertEqual(v1.select, True) # Should be selected
        self.assertEqual(v0.select, False) # Should remain untouched
        bmesh.update_edit_mesh.assert_called()

if __name__ == '__main__':
    unittest.main()
