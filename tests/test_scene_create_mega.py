"""Tests for scene_create mega tool routing and validation."""
import pytest
from unittest.mock import MagicMock, patch


class TestSceneCreateMega:
    """Test scene_create mega tool routing."""

    def setup_method(self):
        self.mock_ctx = MagicMock()

    @patch("server.adapters.mcp.areas.scene._scene_create_light")
    def test_action_light_routes_to_create_light(self, mock_create_light):
        """Test action='light' routes to _scene_create_light."""
        from server.adapters.mcp.areas.scene import scene_create

        mock_create_light.return_value = "Light created"
        result = scene_create.fn(
            self.mock_ctx,
            action="light",
            light_type="SUN",
            energy=5.0,
            location=[0, 0, 5]
        )

        mock_create_light.assert_called_once()
        assert result == "Light created"

    @patch("server.adapters.mcp.areas.scene._scene_create_camera")
    def test_action_camera_routes_to_create_camera(self, mock_create_camera):
        """Test action='camera' routes to _scene_create_camera."""
        from server.adapters.mcp.areas.scene import scene_create

        mock_create_camera.return_value = "Camera created"
        result = scene_create.fn(
            self.mock_ctx,
            action="camera",
            location=[0, -10, 5],
            rotation=[1.0, 0, 0],
            lens=85.0
        )

        mock_create_camera.assert_called_once()
        assert result == "Camera created"

    @patch("server.adapters.mcp.areas.scene._scene_create_empty")
    def test_action_empty_routes_to_create_empty(self, mock_create_empty):
        """Test action='empty' routes to _scene_create_empty."""
        from server.adapters.mcp.areas.scene import scene_create

        mock_create_empty.return_value = "Empty created"
        result = scene_create.fn(
            self.mock_ctx,
            action="empty",
            empty_type="ARROWS",
            location=[0, 0, 2]
        )

        mock_create_empty.assert_called_once()
        assert result == "Empty created"

    def test_invalid_action_returns_error(self):
        """Test invalid action returns helpful error message."""
        from server.adapters.mcp.areas.scene import scene_create

        result = scene_create.fn(self.mock_ctx, action="invalid")

        assert "Unknown action" in result
        assert "invalid" in result
        assert "light" in result
        assert "camera" in result
        assert "empty" in result

    @patch("server.adapters.mcp.areas.scene._scene_create_light")
    def test_light_with_default_params(self, mock_create_light):
        """Test light action works with default parameters."""
        from server.adapters.mcp.areas.scene import scene_create

        mock_create_light.return_value = "Light created"
        result = scene_create.fn(self.mock_ctx, action="light")

        mock_create_light.assert_called_once()
        # Verify default light_type is POINT
        call_args = mock_create_light.call_args
        assert call_args[0][1] == "POINT"  # light_type
