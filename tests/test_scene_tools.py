import unittest
from unittest.mock import MagicMock
import sys
import importlib

# Mock bpy BEFORE importing the module under test
if "bpy" not in sys.modules:
    sys.modules["bpy"] = MagicMock()
import bpy

# Import the module to be tested
import blender_addon.application.handlers.scene

class TestSceneTools(unittest.TestCase):
    def setUp(self):
        # Reload the module to ensure it uses the fresh mock for this test execution
        importlib.reload(blender_addon.application.handlers.scene)
        from blender_addon.application.handlers.scene import SceneHandler
        
        # --- MOCK SETUP ---
        # 1. Objects
        self.cube = MagicMock()
        self.cube.name = "Cube"
        self.cube.type = "MESH"
        self.cube.location = (0, 0, 0)

        self.camera = MagicMock()
        self.camera.name = "Camera"
        self.camera.type = "CAMERA"
        
        self.light = MagicMock()
        self.light.name = "Light"
        self.light.type = "LIGHT"

        # 2. Scene Objects List
        self.scene_objects = [self.cube, self.camera, self.light]
        
        # Setup bpy.context
        bpy.context.scene.objects = self.scene_objects

        # 3. bpy.data.objects Dictionary Behavior
        # Important: Create a new MagicMock for bpy.data.objects for each test
        bpy.data.objects = MagicMock()
        
        def get_object(key):
            for obj in self.scene_objects:
                if obj.name == key:
                    return obj
            raise KeyError(key)
            
        bpy.data.objects.__getitem__.side_effect = get_object
        bpy.data.objects.__contains__.side_effect = lambda k: any(o.name == k for o in self.scene_objects)
        
        # 4. Collections
        bpy.data.collections = []

        # 5. Remove mock
        bpy.data.objects.remove = MagicMock()
        
        # 6. Handler Instance
        self.handler = SceneHandler()

    def test_list_objects(self):
        result = self.handler.list_objects()
        self.assertEqual(len(result), 3)
        names = [r["name"] for r in result]
        self.assertIn("Cube", names)
        self.assertIn("Camera", names)

    def test_delete_object(self):
        self.handler.delete_object("Cube")
        bpy.data.objects.remove.assert_called_with(self.cube, do_unlink=True)

    def test_clean_scene_keep_lights(self):
        # Should only delete Cube (MESH)
        self.handler.clean_scene(keep_lights_and_cameras=True)
        
        # Verify remove called for cube but NOT camera/light
        bpy.data.objects.remove.assert_called_with(self.cube, do_unlink=True)
        
        # Check that remove was NOT called for camera or light
        # Get all args passed to remove
        removed_objects = [call.args[0] for call in bpy.data.objects.remove.call_args_list]
        self.assertIn(self.cube, removed_objects)
        self.assertNotIn(self.camera, removed_objects)
        self.assertNotIn(self.light, removed_objects)

    def test_clean_scene_hard_reset(self):
        # Should delete EVERYTHING
        self.handler.clean_scene(keep_lights_and_cameras=False)
        
        removed_objects = [call.args[0] for call in bpy.data.objects.remove.call_args_list]
        self.assertIn(self.cube, removed_objects)
        self.assertIn(self.camera, removed_objects)
        self.assertIn(self.light, removed_objects)

if __name__ == "__main__":
    unittest.main()
