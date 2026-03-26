import sys
from unittest.mock import MagicMock

from blender_addon.application.handlers.scene import SceneHandler


class TestViewState:
    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]

        self.rv3d = MagicMock()
        self.rv3d.view_location = (1.0, 2.0, 3.0)
        self.rv3d.view_distance = 12.5
        self.rv3d.view_rotation = (1.0, 0.0, 0.0, 0.0)
        self.rv3d.view_perspective = "PERSP"

        self.space = MagicMock()
        self.space.type = "VIEW_3D"
        self.space.region_3d = self.rv3d

        self.area = MagicMock()
        self.area.type = "VIEW_3D"
        self.area.spaces = [self.space]

        self.mock_bpy.context.screen.areas = [self.area]
        self.handler = SceneHandler()

    def test_get_view_state_returns_structured_snapshot(self):
        state = self.handler.get_view_state()

        assert state["available"] is True
        assert state["view_location"] == [1.0, 2.0, 3.0]
        assert state["view_distance"] == 12.5
        assert state["view_rotation"] == [1.0, 0.0, 0.0, 0.0]
        assert state["view_perspective"] == "PERSP"

    def test_restore_view_state_replays_snapshot(self):
        self.handler.restore_view_state(
            {
                "view_location": [4.0, 5.0, 6.0],
                "view_distance": 8.0,
                "view_rotation": [1.0, 0.0, 0.0, 0.0],
                "view_perspective": "ORTHO",
            }
        )

        assert self.rv3d.view_location is not None
        assert self.rv3d.view_distance == 8.0
        assert self.rv3d.view_rotation is not None
        assert self.rv3d.view_perspective == "ORTHO"

    def test_set_standard_view_uses_view_axis_operator(self):
        self.mock_bpy.ops.view3d = MagicMock()
        self.mock_bpy.context.temp_override = MagicMock()
        self.mock_bpy.context.temp_override.return_value.__enter__ = MagicMock()
        self.mock_bpy.context.temp_override.return_value.__exit__ = MagicMock()
        self.area.regions = [MagicMock(type="WINDOW")]

        result = self.handler.set_standard_view("FRONT")

        self.mock_bpy.ops.view3d.view_axis.assert_called_once_with(type="FRONT")
        assert "FRONT" in result
