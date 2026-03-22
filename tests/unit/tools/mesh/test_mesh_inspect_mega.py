"""Tests for mesh_inspect mega tool routing and validation."""

import asyncio
from unittest.mock import MagicMock, patch

from server.adapters.mcp.contracts.mesh import MeshInspectResponseContract


class TestMeshInspectMega:
    """Test mesh_inspect mega tool routing."""

    def setup_method(self):
        self.mock_ctx = MagicMock()

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh._mesh_inspect_summary")
    def test_action_summary_routes_to_summary(self, mock_summary, mock_router_enabled):
        """Test action='summary' routes to _mesh_inspect_summary."""
        from server.adapters.mcp.areas.mesh import mesh_inspect

        callable_mesh_inspect = getattr(mesh_inspect, "fn", mesh_inspect)
        mock_summary.return_value = {"object_name": "Cube", "vertex_count": 8}
        result = asyncio.run(callable_mesh_inspect(self.mock_ctx, action="summary", object_name="Cube"))

        mock_summary.assert_called_once_with(self.mock_ctx, "Cube")
        assert isinstance(result, MeshInspectResponseContract)
        assert result.action == "summary"
        assert result.summary["object_name"] == "Cube"

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh._mesh_get_vertex_data")
    def test_action_vertices_routes_to_vertex_data(self, mock_vertices, mock_router_enabled):
        """Test action='vertices' routes to _mesh_get_vertex_data."""
        from server.adapters.mcp.areas.mesh import mesh_inspect

        callable_mesh_inspect = getattr(mesh_inspect, "fn", mesh_inspect)
        mock_vertices.return_value = {
            "object_name": "Cube",
            "filtered_count": 4,
            "returned_count": 2,
            "offset": 0,
            "limit": 2,
            "has_more": True,
            "vertices": [{"index": 0}, {"index": 1}],
        }
        result = asyncio.run(
            callable_mesh_inspect(
                self.mock_ctx,
                action="vertices",
                object_name="Cube",
                selected_only=True,
            )
        )

        mock_vertices.assert_called_once_with(self.mock_ctx, "Cube", True, None, None)
        assert isinstance(result, MeshInspectResponseContract)
        assert result.action == "vertices"
        assert result.returned == 2
        assert len(result.items) == 2

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh._mesh_get_edge_data")
    def test_action_edges_routes_to_edge_data(self, mock_edges, mock_router_enabled):
        """Test action='edges' routes to _mesh_get_edge_data."""
        from server.adapters.mcp.areas.mesh import mesh_inspect

        callable_mesh_inspect = getattr(mesh_inspect, "fn", mesh_inspect)
        mock_edges.return_value = {
            "object_name": "Cube",
            "filtered_count": 1,
            "returned_count": 1,
            "offset": 0,
            "limit": None,
            "has_more": False,
            "edges": [{"index": 0}],
        }
        result = asyncio.run(callable_mesh_inspect(self.mock_ctx, action="edges", object_name="Cube"))

        mock_edges.assert_called_once_with(self.mock_ctx, "Cube", False, None, None)
        assert isinstance(result, MeshInspectResponseContract)
        assert result.action == "edges"

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh._mesh_get_face_data")
    def test_action_faces_routes_to_face_data(self, mock_faces, mock_router_enabled):
        """Test action='faces' routes to _mesh_get_face_data."""
        from server.adapters.mcp.areas.mesh import mesh_inspect

        callable_mesh_inspect = getattr(mesh_inspect, "fn", mesh_inspect)
        mock_faces.return_value = {
            "object_name": "Cube",
            "filtered_count": 1,
            "returned_count": 1,
            "offset": 0,
            "limit": None,
            "has_more": False,
            "faces": [{"index": 0}],
        }
        result = asyncio.run(callable_mesh_inspect(self.mock_ctx, action="faces", object_name="Cube"))

        mock_faces.assert_called_once_with(self.mock_ctx, "Cube", False, None, None)
        assert isinstance(result, MeshInspectResponseContract)
        assert result.action == "faces"

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh._mesh_get_uv_data")
    def test_action_uvs_routes_to_uv_data(self, mock_uvs, mock_router_enabled):
        """Test action='uvs' routes to _mesh_get_uv_data."""
        from server.adapters.mcp.areas.mesh import mesh_inspect

        callable_mesh_inspect = getattr(mesh_inspect, "fn", mesh_inspect)
        mock_uvs.return_value = {
            "object_name": "Cube",
            "filtered_count": 1,
            "returned_count": 1,
            "offset": 0,
            "limit": None,
            "has_more": False,
            "faces": [{"face_index": 0}],
        }
        result = asyncio.run(
            callable_mesh_inspect(
                self.mock_ctx,
                action="uvs",
                object_name="Cube",
                uv_layer="UVMap",
                selected_only=True,
            )
        )

        mock_uvs.assert_called_once_with(self.mock_ctx, "Cube", "UVMap", True, None, None)
        assert isinstance(result, MeshInspectResponseContract)
        assert result.action == "uvs"

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh._mesh_get_loop_normals")
    def test_action_normals_routes_to_loop_normals(self, mock_normals, mock_router_enabled):
        """Test action='normals' routes to _mesh_get_loop_normals."""
        from server.adapters.mcp.areas.mesh import mesh_inspect

        callable_mesh_inspect = getattr(mesh_inspect, "fn", mesh_inspect)
        mock_normals.return_value = {
            "object_name": "Cube",
            "filtered_count": 1,
            "returned_count": 1,
            "offset": 0,
            "limit": None,
            "has_more": False,
            "loops": [{"loop_index": 0}],
        }
        result = asyncio.run(callable_mesh_inspect(self.mock_ctx, action="normals", object_name="Cube"))

        mock_normals.assert_called_once_with(self.mock_ctx, "Cube", False, None, None)
        assert isinstance(result, MeshInspectResponseContract)
        assert result.action == "normals"

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh._mesh_get_attributes")
    def test_action_attributes_routes_to_attributes(self, mock_attrs, mock_router_enabled):
        """Test action='attributes' routes to _mesh_get_attributes."""
        from server.adapters.mcp.areas.mesh import mesh_inspect

        callable_mesh_inspect = getattr(mesh_inspect, "fn", mesh_inspect)
        mock_attrs.return_value = {
            "object_name": "Cube",
            "filtered_count": 1,
            "returned_count": 1,
            "offset": 0,
            "limit": None,
            "has_more": False,
            "values": [{"index": 0, "value": [1, 0, 0]}],
        }
        result = asyncio.run(
            callable_mesh_inspect(
                self.mock_ctx,
                action="attributes",
                object_name="Cube",
                attribute_name="Col",
                selected_only=True,
            )
        )

        mock_attrs.assert_called_once_with(self.mock_ctx, "Cube", "Col", True, None, None)
        assert isinstance(result, MeshInspectResponseContract)
        assert result.action == "attributes"

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh._mesh_get_shape_keys")
    def test_action_shape_keys_routes_to_shape_keys(self, mock_shape_keys, mock_router_enabled):
        """Test action='shape_keys' routes to _mesh_get_shape_keys."""
        from server.adapters.mcp.areas.mesh import mesh_inspect

        callable_mesh_inspect = getattr(mesh_inspect, "fn", mesh_inspect)
        mock_shape_keys.return_value = {
            "object_name": "Cube",
            "filtered_count": 1,
            "returned_count": 1,
            "offset": 0,
            "limit": None,
            "has_more": False,
            "shape_keys": [{"name": "Key 1"}],
        }
        result = asyncio.run(
            callable_mesh_inspect(
                self.mock_ctx,
                action="shape_keys",
                object_name="Cube",
                include_deltas=True,
            )
        )

        mock_shape_keys.assert_called_once_with(self.mock_ctx, "Cube", True, None, None)
        assert isinstance(result, MeshInspectResponseContract)
        assert result.action == "shape_keys"

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh._mesh_get_vertex_group_weights")
    def test_action_group_weights_routes_to_group_weights(self, mock_groups, mock_router_enabled):
        """Test action='group_weights' routes to _mesh_get_vertex_group_weights."""
        from server.adapters.mcp.areas.mesh import mesh_inspect

        callable_mesh_inspect = getattr(mesh_inspect, "fn", mesh_inspect)
        mock_groups.return_value = {
            "object_name": "Cube",
            "filtered_count": 1,
            "returned_count": 1,
            "offset": 0,
            "limit": None,
            "has_more": False,
            "weights": [{"vert": 1, "weight": 1.0}],
        }
        result = asyncio.run(
            callable_mesh_inspect(
                self.mock_ctx,
                action="group_weights",
                object_name="Cube",
                group_name="Spine",
                selected_only=True,
            )
        )

        mock_groups.assert_called_once_with(self.mock_ctx, "Cube", "Spine", True, None, None)
        assert isinstance(result, MeshInspectResponseContract)
        assert result.action == "group_weights"

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    def test_missing_object_name_returns_error(self, mock_router_enabled):
        """Test missing object_name returns helpful error."""
        from server.adapters.mcp.areas.mesh import mesh_inspect

        callable_mesh_inspect = getattr(mesh_inspect, "fn", mesh_inspect)
        result = asyncio.run(callable_mesh_inspect(self.mock_ctx, action="vertices"))

        assert isinstance(result, MeshInspectResponseContract)
        assert "requires 'object_name'" in result.error

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    def test_invalid_action_returns_error(self, mock_router_enabled):
        """Test invalid action returns helpful error message."""
        from server.adapters.mcp.areas.mesh import mesh_inspect

        callable_mesh_inspect = getattr(mesh_inspect, "fn", mesh_inspect)
        result = asyncio.run(callable_mesh_inspect(self.mock_ctx, action="invalid", object_name="Cube"))

        assert isinstance(result, MeshInspectResponseContract)
        assert "Unknown action" in result.error
        assert "summary" in result.error
        assert "vertices" in result.error
        assert "group_weights" in result.error

    @patch("server.adapters.mcp.areas.mesh.run_inspection_summary_assistant")
    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh._mesh_inspect_summary")
    def test_assistant_summary_attaches_typed_assistant_payload(
        self,
        mock_summary,
        mock_router_enabled,
        mock_assistant,
    ):
        """assistant_summary=True should attach a bounded assistant envelope."""
        from server.adapters.mcp.areas.mesh import mesh_inspect
        from server.adapters.mcp.sampling.result_types import (
            AssistantBudgetContract,
            AssistantRunResult,
            InspectionSummaryContract,
        )

        callable_mesh_inspect = getattr(mesh_inspect, "fn", mesh_inspect)
        mock_summary.return_value = {"object_name": "Cube", "vertex_count": 8}
        mock_assistant.return_value = AssistantRunResult(
            status="success",
            assistant_name="inspection_summarizer",
            message="ok",
            budget=AssistantBudgetContract(
                max_input_chars=1000,
                max_messages=1,
                max_tokens=100,
                tool_budget=0,
            ),
            capability_source="client",
            result=InspectionSummaryContract(
                inspection_action="summary",
                object_name="Cube",
                overview="Quick mesh summary",
                key_findings=["8 vertices"],
            ),
        )

        result = asyncio.run(
            callable_mesh_inspect(
                self.mock_ctx,
                action="summary",
                object_name="Cube",
                assistant_summary=True,
            )
        )

        assert result.assistant is not None
        assert result.assistant.status == "success"
        assert result.assistant.result.overview == "Quick mesh summary"
