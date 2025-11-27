import pytest
from unittest.mock import MagicMock, patch

# Mock bpy
import sys
from types import ModuleType

mock_bpy = MagicMock()
sys.modules["bpy"] = mock_bpy

from blender_addon.application.handlers.scene import SceneHandler

class TestSceneInspectModifiers:
    def setup_method(self):
        self.handler = SceneHandler()
        mock_bpy.reset_mock()

    def test_inspect_modifiers_single_object(self):
        # Mock object
        mock_obj = MagicMock()
        mock_obj.name = "Cube"
        
        # Mock Modifiers
        mod1 = MagicMock()
        mod1.name = "Subsurf"
        mod1.type = 'SUBSURF'
        mod1.show_viewport = True
        mod1.show_render = True
        mod1.levels = 2
        mod1.render_levels = 3
        
        mod2 = MagicMock()
        mod2.name = "Mirror"
        mod2.type = 'MIRROR'
        mod2.show_viewport = False # Disabled in viewport
        mod2.show_render = True
        mod2.use_axis = [True, False, False]
        mod2.mirror_object = None
        
        mock_obj.modifiers = [mod1, mod2]
        
        mock_bpy.data.objects = {"Cube": mock_obj}
        
        result = self.handler.inspect_modifiers("Cube")
        
        assert result["object_count"] == 1
        assert result["modifier_count"] == 2
        
        mods = result["objects"][0]["modifiers"]
        
        # Verify Subsurf
        assert mods[0]["name"] == "Subsurf"
        assert mods[0]["levels"] == 2
        assert mods[0]["render_levels"] == 3
        
        # Verify Mirror
        assert mods[1]["name"] == "Mirror"
        assert mods[1]["use_axis"] == [True, False, False]
        assert mods[1]["show_viewport"] is False

    def test_inspect_modifiers_exclude_disabled(self):
        mock_obj = MagicMock()
        mock_obj.name = "Cube"
        
        mod1 = MagicMock()
        mod1.name = "Visible"
        mod1.show_viewport = True
        mod1.show_render = True
        
        mod2 = MagicMock()
        mod2.name = "Hidden"
        mod2.show_viewport = False
        mod2.show_render = False # Totally disabled
        
        mock_obj.modifiers = [mod1, mod2]
        mock_bpy.data.objects = {"Cube": mock_obj}
        
        result = self.handler.inspect_modifiers("Cube", include_disabled=False)
        
        assert result["modifier_count"] == 1
        assert result["objects"][0]["modifiers"][0]["name"] == "Visible"

    def test_inspect_modifiers_scene_wide(self):
        obj1 = MagicMock(); obj1.name = "Cube"; obj1.modifiers = [MagicMock(name="M1", type="BEVEL", show_viewport=True, show_render=True)]
        obj2 = MagicMock(); obj2.name = "Sphere"; obj2.modifiers = [] # No modifiers
        obj3 = MagicMock(); obj3.name = "Light"; del obj3.modifiers # No modifiers attr
        
        mock_bpy.context.scene.objects = [obj1, obj2, obj3]
        
        result = self.handler.inspect_modifiers(object_name=None)
        
        assert result["object_count"] == 1 # Only Cube has modifiers
        assert result["modifier_count"] == 1
        assert result["objects"][0]["name"] == "Cube"

    def test_object_not_found(self):
        mock_bpy.data.objects = {}
        with pytest.raises(ValueError, match="Object 'Ghost' not found"):
            self.handler.inspect_modifiers("Ghost")
