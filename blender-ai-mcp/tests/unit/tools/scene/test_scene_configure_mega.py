"""Tests for scene_configure mega tool routing and validation."""

from unittest.mock import MagicMock, patch

from server.adapters.mcp.contracts.scene import SceneConfigureResponseContract


class TestSceneConfigureMega:
    """Test scene_configure mega tool routing."""

    def setup_method(self):
        self.mock_ctx = MagicMock()

    @patch("server.adapters.mcp.areas.scene._scene_configure_render_settings")
    def test_action_render_routes_correctly(self, mock_configure_render):
        from server.adapters.mcp.areas.scene import scene_configure

        settings = {"render_engine": "CYCLES"}
        mock_configure_render.return_value = {"render_engine": "CYCLES"}
        callable_scene_configure = getattr(scene_configure, "fn", scene_configure)
        result = callable_scene_configure(self.mock_ctx, action="render", settings=settings)

        mock_configure_render.assert_called_once_with(self.mock_ctx, settings)
        assert isinstance(result, SceneConfigureResponseContract)
        assert result.action == "render"
        assert result.payload["render_engine"] == "CYCLES"

    @patch("server.adapters.mcp.areas.scene._scene_configure_color_management")
    def test_action_color_management_routes_correctly(self, mock_configure_color):
        from server.adapters.mcp.areas.scene import scene_configure

        settings = {"view_transform": "AgX"}
        mock_configure_color.return_value = {"view_transform": "AgX"}
        callable_scene_configure = getattr(scene_configure, "fn", scene_configure)
        result = callable_scene_configure(self.mock_ctx, action="color_management", settings=settings)

        mock_configure_color.assert_called_once_with(self.mock_ctx, settings)
        assert isinstance(result, SceneConfigureResponseContract)
        assert result.action == "color_management"
        assert result.payload["view_transform"] == "AgX"

    @patch("server.adapters.mcp.areas.scene._scene_configure_world")
    def test_action_world_routes_correctly(self, mock_configure_world):
        from server.adapters.mcp.areas.scene import scene_configure

        settings = {"world_name": "Studio"}
        mock_configure_world.return_value = {"world_name": "Studio"}
        callable_scene_configure = getattr(scene_configure, "fn", scene_configure)
        result = callable_scene_configure(self.mock_ctx, action="world", settings=settings)

        mock_configure_world.assert_called_once_with(self.mock_ctx, settings)
        assert isinstance(result, SceneConfigureResponseContract)
        assert result.action == "world"
        assert result.payload["world_name"] == "Studio"

    def test_settings_must_be_mapping(self):
        from server.adapters.mcp.areas.scene import scene_configure

        callable_scene_configure = getattr(scene_configure, "fn", scene_configure)
        result = callable_scene_configure(self.mock_ctx, action="render", settings="invalid")

        assert isinstance(result, SceneConfigureResponseContract)
        assert "settings" in result.error

    def test_invalid_action_returns_error(self):
        from server.adapters.mcp.areas.scene import scene_configure

        callable_scene_configure = getattr(scene_configure, "fn", scene_configure)
        result = callable_scene_configure(self.mock_ctx, action="invalid", settings={})

        assert isinstance(result, SceneConfigureResponseContract)
        assert "Unknown action" in result.error
        assert "render" in result.error
        assert "color_management" in result.error
        assert "world" in result.error
