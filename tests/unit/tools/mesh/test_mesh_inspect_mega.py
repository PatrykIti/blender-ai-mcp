"""Tests for mesh_inspect mega tool routing and validation."""
from unittest.mock import MagicMock, patch


class TestMeshInspectMega:
    """Test mesh_inspect mega tool routing."""

    def setup_method(self):
        self.mock_ctx = MagicMock()

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh._mesh_inspect_summary")
    def test_action_summary_routes_to_summary(self, mock_summary, mock_router_enabled):
        """Test action='summary' routes to _mesh_inspect_summary."""
        from server.adapters.mcp.areas.mesh import mesh_inspect

        mock_summary.return_value = "Summary"
        result = mesh_inspect.fn(self.mock_ctx, action="summary", object_name="Cube")

        mock_summary.assert_called_once_with(self.mock_ctx, "Cube")
        assert result == "Summary"

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh._mesh_get_vertex_data")
    def test_action_vertices_routes_to_vertex_data(self, mock_vertices, mock_router_enabled):
        """Test action='vertices' routes to _mesh_get_vertex_data."""
        from server.adapters.mcp.areas.mesh import mesh_inspect

        mock_vertices.return_value = "Vertices"
        result = mesh_inspect.fn(
            self.mock_ctx,
            action="vertices",
            object_name="Cube",
            selected_only=True,
        )

        mock_vertices.assert_called_once_with(self.mock_ctx, "Cube", True)
        assert result == "Vertices"

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh._mesh_get_edge_data")
    def test_action_edges_routes_to_edge_data(self, mock_edges, mock_router_enabled):
        """Test action='edges' routes to _mesh_get_edge_data."""
        from server.adapters.mcp.areas.mesh import mesh_inspect

        mock_edges.return_value = "Edges"
        result = mesh_inspect.fn(self.mock_ctx, action="edges", object_name="Cube")

        mock_edges.assert_called_once_with(self.mock_ctx, "Cube", False)
        assert result == "Edges"

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh._mesh_get_face_data")
    def test_action_faces_routes_to_face_data(self, mock_faces, mock_router_enabled):
        """Test action='faces' routes to _mesh_get_face_data."""
        from server.adapters.mcp.areas.mesh import mesh_inspect

        mock_faces.return_value = "Faces"
        result = mesh_inspect.fn(self.mock_ctx, action="faces", object_name="Cube")

        mock_faces.assert_called_once_with(self.mock_ctx, "Cube", False)
        assert result == "Faces"

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh._mesh_get_uv_data")
    def test_action_uvs_routes_to_uv_data(self, mock_uvs, mock_router_enabled):
        """Test action='uvs' routes to _mesh_get_uv_data."""
        from server.adapters.mcp.areas.mesh import mesh_inspect

        mock_uvs.return_value = "UVs"
        result = mesh_inspect.fn(
            self.mock_ctx,
            action="uvs",
            object_name="Cube",
            uv_layer="UVMap",
            selected_only=True,
        )

        mock_uvs.assert_called_once_with(self.mock_ctx, "Cube", "UVMap", True)
        assert result == "UVs"

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh._mesh_get_loop_normals")
    def test_action_normals_routes_to_loop_normals(self, mock_normals, mock_router_enabled):
        """Test action='normals' routes to _mesh_get_loop_normals."""
        from server.adapters.mcp.areas.mesh import mesh_inspect

        mock_normals.return_value = "Normals"
        result = mesh_inspect.fn(self.mock_ctx, action="normals", object_name="Cube")

        mock_normals.assert_called_once_with(self.mock_ctx, "Cube", False)
        assert result == "Normals"

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh._mesh_get_attributes")
    def test_action_attributes_routes_to_attributes(self, mock_attrs, mock_router_enabled):
        """Test action='attributes' routes to _mesh_get_attributes."""
        from server.adapters.mcp.areas.mesh import mesh_inspect

        mock_attrs.return_value = "Attributes"
        result = mesh_inspect.fn(
            self.mock_ctx,
            action="attributes",
            object_name="Cube",
            attribute_name="Col",
            selected_only=True,
        )

        mock_attrs.assert_called_once_with(self.mock_ctx, "Cube", "Col", True)
        assert result == "Attributes"

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh._mesh_get_shape_keys")
    def test_action_shape_keys_routes_to_shape_keys(self, mock_shape_keys, mock_router_enabled):
        """Test action='shape_keys' routes to _mesh_get_shape_keys."""
        from server.adapters.mcp.areas.mesh import mesh_inspect

        mock_shape_keys.return_value = "Shape Keys"
        result = mesh_inspect.fn(
            self.mock_ctx,
            action="shape_keys",
            object_name="Cube",
            include_deltas=True,
        )

        mock_shape_keys.assert_called_once_with(self.mock_ctx, "Cube", True)
        assert result == "Shape Keys"

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh._mesh_get_vertex_group_weights")
    def test_action_group_weights_routes_to_group_weights(self, mock_groups, mock_router_enabled):
        """Test action='group_weights' routes to _mesh_get_vertex_group_weights."""
        from server.adapters.mcp.areas.mesh import mesh_inspect

        mock_groups.return_value = "Groups"
        result = mesh_inspect.fn(
            self.mock_ctx,
            action="group_weights",
            object_name="Cube",
            group_name="Spine",
            selected_only=True,
        )

        mock_groups.assert_called_once_with(self.mock_ctx, "Cube", "Spine", True)
        assert result == "Groups"

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    def test_missing_object_name_returns_error(self, mock_router_enabled):
        """Test missing object_name returns helpful error."""
        from server.adapters.mcp.areas.mesh import mesh_inspect

        result = mesh_inspect.fn(self.mock_ctx, action="vertices")

        assert "requires 'object_name'" in result

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    def test_invalid_action_returns_error(self, mock_router_enabled):
        """Test invalid action returns helpful error message."""
        from server.adapters.mcp.areas.mesh import mesh_inspect

        result = mesh_inspect.fn(self.mock_ctx, action="invalid", object_name="Cube")

        assert "Unknown action" in result
        assert "summary" in result
        assert "vertices" in result
        assert "group_weights" in result
