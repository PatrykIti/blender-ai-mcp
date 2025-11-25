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

class TestMeshExtrude(unittest.TestCase):
    def setUp(self):
        self.handler = MeshHandler()
        
        # Reset mocks
        bpy.context.active_object = MagicMock()
        bpy.context.active_object.type = 'MESH'
        bpy.context.mode = 'EDIT_MESH'
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.mesh.extrude_region_move = MagicMock()
        bpy.ops.mesh.edge_face_add = MagicMock()

    def test_extrude_region_no_move(self):
        # Execute
        self.handler.extrude_region()
        
        # Verify
        bpy.ops.mesh.extrude_region_move.assert_called()
        # Verify default arguments are passed
        call_args = bpy.ops.mesh.extrude_region_move.call_args
        self.assertEqual(call_args.kwargs['TRANSFORM_OT_translate']['value'], (0,0,0))

    def test_extrude_region_with_move(self):
        # Execute
        move_vec = [0.0, 0.0, 2.0]
        self.handler.extrude_region(move=move_vec)
        
        # Verify
        bpy.ops.mesh.extrude_region_move.assert_called()
        call_args = bpy.ops.mesh.extrude_region_move.call_args
        self.assertEqual(call_args.kwargs['TRANSFORM_OT_translate']['value'], move_vec)

    def test_fill_holes(self):
        # Execute
        result = self.handler.fill_holes()
        
        # Verify
        bpy.ops.mesh.edge_face_add.assert_called()
        self.assertIn("Filled holes", result)

if __name__ == '__main__':
    unittest.main()
