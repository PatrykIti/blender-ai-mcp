"""Tests for scene_inspect mega tool routing and validation."""
import pytest
from unittest.mock import MagicMock, patch


class TestSceneInspectMega:
    """Test scene_inspect mega tool routing and parameter validation."""

    def setup_method(self):
        self.mock_ctx = MagicMock()

    @patch("server.adapters.mcp.areas.scene._scene_inspect_object")
    def test_action_object_routes_correctly(self, mock_inspect_object):
        """Test action='object' routes to _scene_inspect_object."""
        from server.adapters.mcp.areas.scene import scene_inspect

        mock_inspect_object.return_value = "Object report"
        result = scene_inspect.fn(self.mock_ctx, action="object", object_name="Cube")

        mock_inspect_object.assert_called_once_with(self.mock_ctx, "Cube")
        assert result == "Object report"

    def test_action_object_missing_name_returns_error(self):
        """Test action='object' without object_name returns error."""
        from server.adapters.mcp.areas.scene import scene_inspect

        result = scene_inspect.fn(self.mock_ctx, action="object")

        assert "Error" in result
        assert "object_name" in result

    @patch("server.adapters.mcp.areas.scene._scene_inspect_mesh_topology")
    def test_action_topology_routes_correctly(self, mock_inspect_topology):
        """Test action='topology' routes to _scene_inspect_mesh_topology."""
        from server.adapters.mcp.areas.scene import scene_inspect

        mock_inspect_topology.return_value = "Topology report"
        result = scene_inspect.fn(
            self.mock_ctx,
            action="topology",
            object_name="Cube",
            detailed=True
        )

        mock_inspect_topology.assert_called_once_with(self.mock_ctx, "Cube", True)
        assert result == "Topology report"

    def test_action_topology_missing_name_returns_error(self):
        """Test action='topology' without object_name returns error."""
        from server.adapters.mcp.areas.scene import scene_inspect

        result = scene_inspect.fn(self.mock_ctx, action="topology")

        assert "Error" in result
        assert "object_name" in result

    @patch("server.adapters.mcp.areas.scene._scene_inspect_modifiers")
    def test_action_modifiers_routes_correctly(self, mock_inspect_modifiers):
        """Test action='modifiers' routes to _scene_inspect_modifiers."""
        from server.adapters.mcp.areas.scene import scene_inspect

        mock_inspect_modifiers.return_value = "Modifiers report"
        result = scene_inspect.fn(
            self.mock_ctx,
            action="modifiers",
            object_name="Cube",
            include_disabled=False
        )

        mock_inspect_modifiers.assert_called_once_with(self.mock_ctx, "Cube", False)
        assert result == "Modifiers report"

    @patch("server.adapters.mcp.areas.scene._scene_inspect_modifiers")
    def test_action_modifiers_without_object_name_scans_all(self, mock_inspect_modifiers):
        """Test action='modifiers' without object_name scans all objects."""
        from server.adapters.mcp.areas.scene import scene_inspect

        mock_inspect_modifiers.return_value = "All modifiers report"
        result = scene_inspect.fn(self.mock_ctx, action="modifiers")

        mock_inspect_modifiers.assert_called_once_with(self.mock_ctx, None, True)
        assert result == "All modifiers report"

    @patch("server.adapters.mcp.areas.scene._scene_inspect_material_slots")
    def test_action_materials_routes_correctly(self, mock_inspect_materials):
        """Test action='materials' routes to _scene_inspect_material_slots."""
        from server.adapters.mcp.areas.scene import scene_inspect

        mock_inspect_materials.return_value = "Materials report"
        result = scene_inspect.fn(
            self.mock_ctx,
            action="materials",
            material_filter="Wood",
            include_empty_slots=False
        )

        mock_inspect_materials.assert_called_once_with(self.mock_ctx, "Wood", False)
        assert result == "Materials report"

    @patch("server.adapters.mcp.areas.scene._scene_inspect_material_slots")
    def test_action_materials_with_defaults(self, mock_inspect_materials):
        """Test action='materials' works with default parameters."""
        from server.adapters.mcp.areas.scene import scene_inspect

        mock_inspect_materials.return_value = "Materials report"
        result = scene_inspect.fn(self.mock_ctx, action="materials")

        mock_inspect_materials.assert_called_once_with(self.mock_ctx, None, True)
        assert result == "Materials report"

    @patch("server.adapters.mcp.areas.scene._scene_get_constraints")
    def test_action_constraints_routes_correctly(self, mock_get_constraints):
        """Test action='constraints' routes to _scene_get_constraints."""
        from server.adapters.mcp.areas.scene import scene_inspect

        mock_get_constraints.return_value = "Constraints report"
        result = scene_inspect.fn(
            self.mock_ctx,
            action="constraints",
            object_name="Rig",
            include_bones=True
        )

        mock_get_constraints.assert_called_once_with(self.mock_ctx, "Rig", True)
        assert result == "Constraints report"

    @patch("server.adapters.mcp.areas.scene._scene_inspect_modifier_data")
    def test_action_modifier_data_routes_correctly(self, mock_modifier_data):
        """Test action='modifier_data' routes to _scene_inspect_modifier_data."""
        from server.adapters.mcp.areas.scene import scene_inspect

        mock_modifier_data.return_value = "Modifier data"
        result = scene_inspect.fn(
            self.mock_ctx,
            action="modifier_data",
            object_name="Cube",
            modifier_name="Bevel",
            include_node_tree=True
        )

        mock_modifier_data.assert_called_once_with(self.mock_ctx, "Cube", "Bevel", True)
        assert result == "Modifier data"

    def test_invalid_action_returns_error(self):
        """Test invalid action returns helpful error message."""
        from server.adapters.mcp.areas.scene import scene_inspect

        result = scene_inspect.fn(self.mock_ctx, action="invalid")

        assert "Unknown action" in result
        assert "invalid" in result
        assert "object" in result
        assert "topology" in result
        assert "modifiers" in result
        assert "materials" in result
        assert "constraints" in result
        assert "modifier_data" in result
