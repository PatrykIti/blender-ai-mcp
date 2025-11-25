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

class TestMeshEdges(unittest.TestCase):
    def setUp(self):
        self.handler = MeshHandler()
        
        # Reset mocks
        bpy.context.active_object = MagicMock()
        bpy.context.active_object.type = 'MESH'
        bpy.context.mode = 'EDIT_MESH'
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.mesh.bevel = MagicMock()
        bpy.ops.mesh.subdivide = MagicMock()
        bpy.ops.mesh.inset = MagicMock()

    def test_bevel(self):
        # Execute
        self.handler.bevel(offset=0.2, segments=2)
        
        # Verify
        bpy.ops.mesh.bevel.assert_called_with(offset=0.2, segments=2, profile=0.5, affect='EDGES')

    def test_inset(self):
        # Execute
        self.handler.inset(thickness=0.1, depth=0.05)
        
        # Verify
        bpy.ops.mesh.inset.assert_called_with(thickness=0.1, depth=0.05)

    def test_loop_cut_subdivide_fallback(self):
        # Execute
        # Since loop cut is complex via API, we currently fallback to subdivide for simple cuts
        self.handler.loop_cut(number_cuts=2)
        
        # Verify
        bpy.ops.mesh.subdivide.assert_called_with(number_cuts=2, smoothness=0.0)

if __name__ == '__main__':
    unittest.main()
