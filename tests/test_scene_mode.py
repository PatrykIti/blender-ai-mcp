import sys
import pytest
from unittest.mock import MagicMock

# conftest.py handles bpy mocking
from blender_addon.application.handlers.scene import SceneHandler

class TestSceneMode:
    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]
        self.handler = SceneHandler()
        # Reset mocks
        self.cube = MagicMock()
        self.cube.name = "Cube"
        self.cube.type = "MESH"
        self.cube.location = (0.0, 0.0, 0.0)
        self.cube.rotation_euler = (0.0, 0.0, 0.0)
        self.cube.scale = (1.0, 1.0, 1.0)
        self.cube.dimensions = (2.0, 2.0, 2.0)
        self.cube.users_collection = []
        self.cube.material_slots = []
        self.cube.modifiers = []
        self.cube.keys = MagicMock(return_value=[])
        self.cube.get = MagicMock()
        self.cube.evaluated_get = MagicMock(return_value=self.cube)
        self.light = MagicMock()
        self.light.name = "Light"

        self.mock_bpy.context.mode = 'OBJECT'
        self.mock_bpy.ops.object.mode_set = MagicMock()
        self.mock_bpy.context.active_object = self.cube
        self.mock_bpy.context.selected_objects = [self.cube, self.light]
        self.mock_bpy.data.objects = {"Cube": self.cube}

    def test_set_mode_valid(self):
        # Execute
        result = self.handler.set_mode('EDIT')
        
        # Verify
        self.mock_bpy.ops.object.mode_set.assert_called_with(mode='EDIT')
        assert "Switched to EDIT mode" in result

    def test_set_mode_already_set(self):
        # Setup
        self.mock_bpy.context.mode = 'EDIT'
        
        # Execute
        result = self.handler.set_mode('EDIT')
        
        # Verify
        self.mock_bpy.ops.object.mode_set.assert_not_called()
        assert "Already in EDIT mode" in result

    def test_set_mode_no_active_object(self):
        # Setup
        self.mock_bpy.context.active_object = None

        # Execute & Verify
        with pytest.raises(ValueError):
            self.handler.set_mode('EDIT')

    def test_get_mode_returns_selection_summary(self):
        self.mock_bpy.context.mode = 'EDIT_MESH'
        result = self.handler.get_mode()
        assert result["mode"] == 'EDIT_MESH'
        assert result["active_object"] == 'Cube'
        assert result["active_object_type"] == 'MESH'
        assert result["selection_count"] == 2
        assert 'Cube' in result["selected_object_names"]
        assert 'Light' in result["selected_object_names"]

    def test_list_selection_object_mode(self):
        self.mock_bpy.context.mode = 'OBJECT'
        summary = self.handler.list_selection()
        assert summary["mode"] == 'OBJECT'
        assert summary["selection_count"] == 2
        assert summary["edit_mode_vertex_count"] is None

    def test_inspect_object_basic(self):
        self.cube.type = 'LIGHT'
        report = self.handler.inspect_object("Cube")
        assert report["object_name"] == "Cube"
        assert report["material_slots"] == []

    def test_inspect_object_missing(self):
        self.mock_bpy.data.objects = {}
        with pytest.raises(ValueError):
            self.handler.inspect_object("Missing")

