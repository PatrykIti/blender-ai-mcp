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

class TestMeshAdvanced(unittest.TestCase):
    def setUp(self):
        self.handler = MeshHandler()
        
        # Reset mocks
        bpy.context.active_object = MagicMock()
        bpy.context.active_object.type = 'MESH'
        bpy.context.mode = 'EDIT_MESH'
        bpy.ops.object.mode_set = MagicMock()
        
        # Ops mocks
        bpy.ops.mesh.intersect_boolean = MagicMock()
        bpy.ops.mesh.remove_doubles = MagicMock()
        bpy.ops.mesh.subdivide = MagicMock()

    def test_boolean(self):
        # Execute
        self.handler.boolean(operation='UNION', solver='EXACT')
        
        # Verify
        bpy.ops.mesh.intersect_boolean.assert_called_with(operation='UNION', solver='EXACT')

    def test_merge_by_distance(self):
        # Execute
        self.handler.merge_by_distance(distance=0.01)
        
        # Verify
        bpy.ops.mesh.remove_doubles.assert_called_with(threshold=0.01)

    def test_subdivide(self):
        # Execute
        self.handler.subdivide(number_cuts=3, smoothness=0.5)
        
        # Verify
        bpy.ops.mesh.subdivide.assert_called_with(number_cuts=3, smoothness=0.5)

if __name__ == '__main__':
    unittest.main()
