import sys
from unittest.mock import MagicMock

from blender_addon.application.handlers.scene import SceneHandler


class TestSnapshotStateVisibility:
    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]

        self.visible_cube = MagicMock()
        self.visible_cube.name = "VisibleCube"
        self.visible_cube.type = "MESH"
        self.visible_cube.location = (0, 0, 0)
        self.visible_cube.rotation_euler = (0, 0, 0)
        self.visible_cube.scale = (1, 1, 1)
        self.visible_cube.parent = None
        self.visible_cube.hide_viewport = False
        self.visible_cube.select_get.return_value = False
        self.visible_cube.users_collection = []
        self.visible_cube.modifiers = []
        self.visible_cube.material_slots = []

        self.hidden_cube = MagicMock()
        self.hidden_cube.name = "HiddenCube"
        self.hidden_cube.type = "MESH"
        self.hidden_cube.location = (0, 0, 0)
        self.hidden_cube.rotation_euler = (0, 0, 0)
        self.hidden_cube.scale = (1, 1, 1)
        self.hidden_cube.parent = None
        self.hidden_cube.hide_viewport = True
        self.hidden_cube.select_get.return_value = False
        self.hidden_cube.users_collection = []
        self.hidden_cube.modifiers = []
        self.hidden_cube.material_slots = []

        self.mock_bpy.context.scene.objects = [self.visible_cube, self.hidden_cube]
        self.mock_bpy.context.active_object = None
        self.mock_bpy.context.mode = "OBJECT"

        self.handler = SceneHandler()

    def test_snapshot_state_reports_viewport_hidden_objects_as_not_visible(self):
        result = self.handler.snapshot_state(include_mesh_stats=False, include_materials=False)

        objects = {item["name"]: item for item in result["snapshot"]["objects"]}

        assert objects["VisibleCube"]["visible"] is True
        assert objects["HiddenCube"]["visible"] is False
