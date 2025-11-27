import unittest
from unittest.mock import MagicMock
import sys

# Mock blender modules
if 'bpy' not in sys.modules:
    sys.modules['bpy'] = MagicMock()
if 'bmesh' not in sys.modules:
    sys.modules['bmesh'] = MagicMock()

import bpy
import bmesh
from blender_addon.application.handlers.mesh import MeshHandler

class TestMeshContext(unittest.TestCase):
    def setUp(self):
        self.handler = MeshHandler()
        
        # Reset mocks
        self.mock_obj = MagicMock()
        self.mock_obj.type = 'MESH'
        self.mock_obj.mode = 'OBJECT' # Start in object mode
        self.mock_obj.data = MagicMock()
        
        # Mock context attributes
        bpy.context.active_object = self.mock_obj
        # bpy.context.mode is read-only in real Blender but mockable here
        bpy.context.mode = 'OBJECT' 
        bpy.context.view_layer.objects.active = self.mock_obj
        
        # Mock operators
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.mesh.intersect_boolean = MagicMock()
        bpy.ops.mesh.vertices_smooth = MagicMock()
        bpy.ops.transform.resize = MagicMock()
        
        # BMesh mock
        self.mock_bm = MagicMock()
        self.mock_bm.verts = [MagicMock(), MagicMock()]
        for v in self.mock_bm.verts:
            v.select = True # Select all
        
        bmesh.from_edit_mesh = MagicMock(return_value=self.mock_bm)

    def test_ensure_edit_mode_returns_previous(self):
        # Setup: Object mode
        self.mock_obj.mode = 'OBJECT'
        
        obj, prev = self.handler._ensure_edit_mode()
        
        # It should have switched to EDIT
        bpy.ops.object.mode_set.assert_called_with(mode='EDIT')
        self.assertEqual(prev, 'OBJECT')

    def test_smooth_vertices_restores_mode(self):
        # Setup: Object mode
        self.mock_obj.mode = 'OBJECT'
        
        # Execute
        self.handler.smooth_vertices(iterations=1, factor=0.5)
        
        # Verify
        # 1. Switch to EDIT
        calls = bpy.ops.object.mode_set.call_args_list
        self.assertEqual(calls[0][1]['mode'], 'EDIT')
        
        # 2. Perform Op
        bpy.ops.mesh.vertices_smooth.assert_called()
        
        # 3. Restore OBJECT
        self.assertEqual(calls[-1][1]['mode'], 'OBJECT')

    def test_flatten_vertices_restores_mode(self):
        # Setup: Object mode
        self.mock_obj.mode = 'OBJECT'
        
        # Execute
        self.handler.flatten_vertices(axis='Z')
        
        # Verify
        calls = bpy.ops.object.mode_set.call_args_list
        self.assertEqual(calls[0][1]['mode'], 'EDIT')
        bpy.ops.transform.resize.assert_called()
        self.assertEqual(calls[-1][1]['mode'], 'OBJECT')

    def test_boolean_default_solver(self):
        # Setup: Already in Edit mode
        self.mock_obj.mode = 'EDIT' 
        
        self.handler.boolean()
        
        bpy.ops.mesh.intersect_boolean.assert_called_with(operation='DIFFERENCE', solver='EXACT')

if __name__ == '__main__':
    unittest.main()
