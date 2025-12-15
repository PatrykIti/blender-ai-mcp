"""Tests for MCP material_create vector/color parsing (TASK-064)."""

from unittest.mock import MagicMock, patch


class TestMaterialCreateMcpParsing:
    def setup_method(self):
        self.mock_ctx = MagicMock()

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.material.get_material_handler")
    def test_parses_string_color_params(self, mock_get_material_handler, _mock_router_enabled):
        from server.adapters.mcp.areas.material import material_create

        handler = MagicMock()
        handler.create_material.return_value = "Created"
        mock_get_material_handler.return_value = handler

        result = material_create.fn(
            self.mock_ctx,
            name="Mat",
            base_color="[0.1, 0.2, 0.3, 1]",
            emission_color="[1, 0, 0]",
            emission_strength=2.5,
            alpha=0.8,
        )

        handler.create_material.assert_called_once_with(
            name="Mat",
            base_color=[0.1, 0.2, 0.3, 1.0],
            metallic=0.0,
            roughness=0.5,
            emission_color=[1.0, 0.0, 0.0],
            emission_strength=2.5,
            alpha=0.8,
        )
        assert result == "Created"

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.material.get_material_handler")
    def test_invalid_string_returns_error(self, mock_get_material_handler, _mock_router_enabled):
        from server.adapters.mcp.areas.material import material_create

        handler = MagicMock()
        handler.create_material.return_value = "Created"
        mock_get_material_handler.return_value = handler

        result = material_create.fn(self.mock_ctx, name="Mat", base_color="invalid")

        handler.create_material.assert_not_called()
        assert "Invalid coordinate format" in result

