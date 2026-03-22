"""Tests for scene_inspect mega tool routing and validation."""

import asyncio
from unittest.mock import MagicMock, patch

from server.adapters.mcp.contracts.scene import SceneInspectResponseContract


class TestSceneInspectMega:
    """Test scene_inspect mega tool routing and parameter validation."""

    def setup_method(self):
        self.mock_ctx = MagicMock()

    @patch("server.adapters.mcp.areas.scene._scene_inspect_object")
    def test_action_object_routes_correctly(self, mock_inspect_object):
        """Test action='object' routes to _scene_inspect_object."""
        from server.adapters.mcp.areas.scene import scene_inspect

        callable_scene_inspect = getattr(scene_inspect, "fn", scene_inspect)
        mock_inspect_object.return_value = {"object_name": "Cube", "type": "MESH"}
        result = asyncio.run(callable_scene_inspect(self.mock_ctx, action="object", object_name="Cube"))

        mock_inspect_object.assert_called_once_with(self.mock_ctx, "Cube")
        assert isinstance(result, SceneInspectResponseContract)
        assert result.action == "object"
        assert result.payload["object_name"] == "Cube"

    def test_action_object_missing_name_returns_error(self):
        """Test action='object' without object_name returns error."""
        from server.adapters.mcp.areas.scene import scene_inspect

        callable_scene_inspect = getattr(scene_inspect, "fn", scene_inspect)
        result = asyncio.run(callable_scene_inspect(self.mock_ctx, action="object"))

        assert isinstance(result, SceneInspectResponseContract)
        assert "object_name" in result.error

    @patch("server.adapters.mcp.areas.scene._scene_inspect_mesh_topology")
    def test_action_topology_routes_correctly(self, mock_inspect_topology):
        """Test action='topology' routes to _scene_inspect_mesh_topology."""
        from server.adapters.mcp.areas.scene import scene_inspect

        callable_scene_inspect = getattr(scene_inspect, "fn", scene_inspect)
        mock_inspect_topology.return_value = {"object_name": "Cube", "vertex_count": 8}
        result = asyncio.run(
            callable_scene_inspect(
                self.mock_ctx,
                action="topology",
                object_name="Cube",
                detailed=True,
            )
        )

        mock_inspect_topology.assert_called_once_with(self.mock_ctx, "Cube", True)
        assert isinstance(result, SceneInspectResponseContract)
        assert result.action == "topology"
        assert result.payload["object_name"] == "Cube"

    def test_action_topology_missing_name_returns_error(self):
        """Test action='topology' without object_name returns error."""
        from server.adapters.mcp.areas.scene import scene_inspect

        callable_scene_inspect = getattr(scene_inspect, "fn", scene_inspect)
        result = asyncio.run(callable_scene_inspect(self.mock_ctx, action="topology"))

        assert isinstance(result, SceneInspectResponseContract)
        assert "object_name" in result.error

    @patch("server.adapters.mcp.areas.scene._scene_inspect_modifiers")
    def test_action_modifiers_routes_correctly(self, mock_inspect_modifiers):
        """Test action='modifiers' routes to _scene_inspect_modifiers."""
        from server.adapters.mcp.areas.scene import scene_inspect

        callable_scene_inspect = getattr(scene_inspect, "fn", scene_inspect)
        mock_inspect_modifiers.return_value = {"modifier_count": 1}
        result = asyncio.run(
            callable_scene_inspect(
                self.mock_ctx,
                action="modifiers",
                object_name="Cube",
                include_disabled=False,
            )
        )

        mock_inspect_modifiers.assert_called_once_with(self.mock_ctx, "Cube", False)
        assert isinstance(result, SceneInspectResponseContract)
        assert result.action == "modifiers"

    @patch("server.adapters.mcp.areas.scene._scene_inspect_modifiers")
    def test_action_modifiers_without_object_name_scans_all(self, mock_inspect_modifiers):
        """Test action='modifiers' without object_name scans all objects."""
        from server.adapters.mcp.areas.scene import scene_inspect

        callable_scene_inspect = getattr(scene_inspect, "fn", scene_inspect)
        mock_inspect_modifiers.return_value = {"modifier_count": 0}
        result = asyncio.run(callable_scene_inspect(self.mock_ctx, action="modifiers"))

        mock_inspect_modifiers.assert_called_once_with(self.mock_ctx, None, True)
        assert isinstance(result, SceneInspectResponseContract)

    @patch("server.adapters.mcp.areas.scene._scene_inspect_material_slots")
    def test_action_materials_routes_correctly(self, mock_inspect_materials):
        """Test action='materials' routes to _scene_inspect_material_slots."""
        from server.adapters.mcp.areas.scene import scene_inspect

        callable_scene_inspect = getattr(scene_inspect, "fn", scene_inspect)
        mock_inspect_materials.return_value = {"total_slots": 3}
        result = asyncio.run(
            callable_scene_inspect(
                self.mock_ctx,
                action="materials",
                material_filter="Wood",
                include_empty_slots=False,
            )
        )

        mock_inspect_materials.assert_called_once_with(self.mock_ctx, "Wood", False)
        assert isinstance(result, SceneInspectResponseContract)
        assert result.action == "materials"

    @patch("server.adapters.mcp.areas.scene._scene_inspect_material_slots")
    def test_action_materials_with_defaults(self, mock_inspect_materials):
        """Test action='materials' works with default parameters."""
        from server.adapters.mcp.areas.scene import scene_inspect

        callable_scene_inspect = getattr(scene_inspect, "fn", scene_inspect)
        mock_inspect_materials.return_value = {"total_slots": 0}
        result = asyncio.run(callable_scene_inspect(self.mock_ctx, action="materials"))

        mock_inspect_materials.assert_called_once_with(self.mock_ctx, None, True)
        assert isinstance(result, SceneInspectResponseContract)

    @patch("server.adapters.mcp.areas.scene._scene_get_constraints")
    def test_action_constraints_routes_correctly(self, mock_get_constraints):
        """Test action='constraints' routes to _scene_get_constraints."""
        from server.adapters.mcp.areas.scene import scene_inspect

        callable_scene_inspect = getattr(scene_inspect, "fn", scene_inspect)
        mock_get_constraints.return_value = {"constraints": []}
        result = asyncio.run(
            callable_scene_inspect(
                self.mock_ctx,
                action="constraints",
                object_name="Rig",
                include_bones=True,
            )
        )

        mock_get_constraints.assert_called_once_with(self.mock_ctx, "Rig", True)
        assert isinstance(result, SceneInspectResponseContract)
        assert result.action == "constraints"

    @patch("server.adapters.mcp.areas.scene._scene_inspect_modifier_data")
    def test_action_modifier_data_routes_correctly(self, mock_modifier_data):
        """Test action='modifier_data' routes to _scene_inspect_modifier_data."""
        from server.adapters.mcp.areas.scene import scene_inspect

        callable_scene_inspect = getattr(scene_inspect, "fn", scene_inspect)
        mock_modifier_data.return_value = {"modifier_name": "Bevel"}
        result = asyncio.run(
            callable_scene_inspect(
                self.mock_ctx,
                action="modifier_data",
                object_name="Cube",
                modifier_name="Bevel",
                include_node_tree=True,
            )
        )

        mock_modifier_data.assert_called_once_with(self.mock_ctx, "Cube", "Bevel", True)
        assert isinstance(result, SceneInspectResponseContract)
        assert result.action == "modifier_data"

    def test_invalid_action_returns_error(self):
        """Test invalid action returns helpful error message."""
        from server.adapters.mcp.areas.scene import scene_inspect

        callable_scene_inspect = getattr(scene_inspect, "fn", scene_inspect)
        result = asyncio.run(callable_scene_inspect(self.mock_ctx, action="invalid"))

        assert isinstance(result, SceneInspectResponseContract)
        assert "Unknown action" in result.error
        assert "invalid" in result.error
        assert "object" in result.error
        assert "topology" in result.error
        assert "modifiers" in result.error
        assert "materials" in result.error
        assert "constraints" in result.error
        assert "modifier_data" in result.error

    @patch("server.adapters.mcp.areas.scene.run_inspection_summary_assistant")
    @patch("server.adapters.mcp.areas.scene._scene_inspect_object")
    def test_assistant_summary_attaches_typed_assistant_payload(
        self,
        mock_inspect_object,
        mock_assistant,
    ):
        """assistant_summary=True should attach a bounded assistant envelope."""
        from server.adapters.mcp.areas.scene import scene_inspect
        from server.adapters.mcp.sampling.result_types import (
            AssistantBudgetContract,
            AssistantRunResult,
            InspectionSummaryContract,
        )

        callable_scene_inspect = getattr(scene_inspect, "fn", scene_inspect)
        mock_inspect_object.return_value = {"object_name": "Cube", "type": "MESH"}
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
                inspection_action="object",
                object_name="Cube",
                overview="Cube overview",
                key_findings=["Mesh object"],
            ),
        )

        result = asyncio.run(
            callable_scene_inspect(
                self.mock_ctx,
                action="object",
                object_name="Cube",
                assistant_summary=True,
            )
        )

        assert result.assistant is not None
        assert result.assistant.status == "success"
        assert result.assistant.result.overview == "Cube overview"
