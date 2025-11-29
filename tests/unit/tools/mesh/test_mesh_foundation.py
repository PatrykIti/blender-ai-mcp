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
        # Setup BMesh mock
        bm = MagicMock()
        bmesh.from_edit_mesh.return_value = bm
        
        # Mock faces list
        f1 = MagicMock(); f1.select = True
        f2 = MagicMock(); f2.select = False
        
        # Mock sequence behavior for bm.faces
        mock_faces_seq = MagicMock()
        mock_faces_seq.__iter__.return_value = iter([f1, f2])
        bm.faces = mock_faces_seq
        
        # Mock bmesh.ops
        bmesh.ops = MagicMock()
        bmesh.ops.delete = MagicMock()

        # Execute
        self.handler.delete_selected(type='FACE')
        
        # Verify
        # 1. Ensure Edit Mode (implicit in _get_bmesh)
        bmesh.from_edit_mesh.assert_called()
        
        # 2. Verify bmesh.ops.delete called with correct context and geom
        bmesh.ops.delete.assert_called()
        call_args = bmesh.ops.delete.call_args
        self.assertEqual(call_args.kwargs['context'], 'FACES')
        self.assertEqual(call_args.kwargs['geom'], [f1]) # Only selected face
        
        # 3. Verify update
        bmesh.update_edit_mesh.assert_called()

    def test_select_by_index_set_mode(self):
        # Setup BMesh mock structure
        bm = MagicMock()
        
        mock_verts_seq = MagicMock()
        v0 = MagicMock(); v0.select = False
        v1 = MagicMock(); v1.select = False
        items = [v0, v1]
        
        mock_verts_seq.__getitem__.side_effect = items.__getitem__
        mock_verts_seq.__len__.side_effect = items.__len__
        
        bm.verts = mock_verts_seq
        bm.edges = MagicMock()
        bm.faces = MagicMock()
        
        bmesh.from_edit_mesh.return_value = bm
        
        # Execute: Select vertex at index 1 in SET mode
        self.handler.select_by_index(indices=[1], type='VERT', selection_mode='SET')
        
        # Verify
        # 1. Ensure deselect all was called (because of SET mode)
        bpy.ops.mesh.select_all.assert_called_with(action='DESELECT')
        
        # 2. Verify bmesh operations
        bmesh.from_edit_mesh.assert_called()
        self.assertEqual(v1.select, True) # Should be selected
        self.assertEqual(v0.select, False) # Should remain untouched
        bmesh.update_edit_mesh.assert_called()

    def test_select_by_index_add_mode(self):
        # Setup BMesh mock structure
        bm = MagicMock()
        mock_verts_seq = MagicMock()
        v0 = MagicMock(); v0.select = True # Already selected
        v1 = MagicMock(); v1.select = False
        items = [v0, v1]
        
        mock_verts_seq.__getitem__.side_effect = items.__getitem__
        mock_verts_seq.__len__.side_effect = items.__len__
        bm.verts = mock_verts_seq
        bm.edges = MagicMock()
        bm.faces = MagicMock()
        bmesh.from_edit_mesh.return_value = bm
        
        # Execute: ADD vertex 1 to selection
        self.handler.select_by_index(indices=[1], type='VERT', selection_mode='ADD')
        
        # Verify:
        # Deselect all should NOT be called
        bpy.ops.mesh.select_all.assert_not_called()
        
        self.assertEqual(v0.select, True) # Should remain selected
        self.assertEqual(v1.select, True) # Should become selected

    def test_select_by_index_subtract_mode(self):
        # Setup BMesh mock structure
        bm = MagicMock()
        mock_verts_seq = MagicMock()
        v0 = MagicMock(); v0.select = True
        items = [v0]
        mock_verts_seq.__getitem__.side_effect = items.__getitem__
        mock_verts_seq.__len__.side_effect = items.__len__
        bm.verts = mock_verts_seq
        bm.edges = MagicMock()
        bm.faces = MagicMock()
        bmesh.from_edit_mesh.return_value = bm
        
        # Execute: SUBTRACT vertex 0
        self.handler.select_by_index(indices=[0], type='VERT', selection_mode='SUBTRACT')
        
        # Verify
        bpy.ops.mesh.select_all.assert_not_called()
        self.assertEqual(v0.select, False) # Should become deselected

if __name__ == '__main__':
    unittest.main()
