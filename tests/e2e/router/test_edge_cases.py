"""
E2E tests for Router Edge Cases.

Tests handling of unusual scenarios and boundary conditions.
Requires running Blender instance.

TASK-040
"""

import pytest

from server.router.application.router import SupervisorRouter
from server.router.infrastructure.config import RouterConfig


class TestNoActiveObject:
    """Tests for operations without active object."""

    def test_mesh_operation_without_object_handles_gracefully(self, router, rpc_client, clean_scene):
        """Test: Mesh operation on empty scene doesn't crash."""
        # Scene is empty after clean_scene, no active object

        # Try mesh operation - should handle gracefully
        tools = router.process_llm_tool_call(
            "mesh_extrude_region",
            {"depth": 0.5}
        )

        # Should return list (possibly empty or with error info)
        assert isinstance(tools, list)

    def test_modeling_operation_without_object_handles_gracefully(self, router, rpc_client, clean_scene):
        """Test: Modeling operation without active object."""
        # Scene is empty

        tools = router.process_llm_tool_call(
            "modeling_transform_object",
            {"location": [1, 0, 0]}
        )

        assert isinstance(tools, list)


class TestMultipleSelectedObjects:
    """Tests for operations with multiple selected objects."""

    def test_transform_with_multiple_selected(self, router, rpc_client, clean_scene):
        """Test: Transform with multiple objects selected."""
        # Create multiple objects
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "SPHERE"})

        # Select both (sphere is active after creation, extend to select cube too)
        rpc_client.send_request("scene.select_object", {"name": "Cube", "extend": True})

        router.invalidate_cache()

        tools = router.process_llm_tool_call(
            "modeling_transform_object",
            {"scale": [2.0, 2.0, 2.0]}
        )

        assert isinstance(tools, list)
        assert len(tools) > 0

    def test_modifier_with_multiple_selected(self, router, rpc_client, clean_scene):
        """Test: Adding modifier with multiple objects selected."""
        # Create multiple objects
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})

        router.invalidate_cache()

        tools = router.process_llm_tool_call(
            "modeling_add_modifier",
            {"modifier_type": "BEVEL", "width": 0.1}
        )

        assert isinstance(tools, list)


class TestModeTransitions:
    """Tests for mode transition edge cases."""

    def test_edit_mode_tool_from_sculpt_mode(self, router, rpc_client, clean_scene):
        """Test: Edit mode tool called from Sculpt mode."""
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})

        # Enter sculpt mode
        try:
            rpc_client.send_request("system.set_mode", {"mode": "SCULPT"})
        except Exception:
            # Sculpt mode may not be available, skip this scenario
            pytest.skip("Sculpt mode not available")

        router.invalidate_cache()

        # Try edit mode tool
        tools = router.process_llm_tool_call(
            "mesh_subdivide",
            {"number_cuts": 2}
        )

        tool_names = [t["tool"] for t in tools]

        # Should have mode switch
        assert isinstance(tools, list)
        if len(tools) > 1:
            assert "system_set_mode" in tool_names

    def test_object_mode_tool_from_edit_mode(self, router, rpc_client, clean_scene):
        """Test: Object mode tool called from Edit mode."""
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})

        router.invalidate_cache()

        # Try object mode tool
        tools = router.process_llm_tool_call(
            "modeling_add_modifier",
            {"modifier_type": "SUBSURF", "levels": 2}
        )

        tool_names = [t["tool"] for t in tools]

        # Should have mode switch
        assert isinstance(tools, list)
        if len(tools) > 1:
            assert "system_set_mode" in tool_names


class TestInvalidParameters:
    """Tests for invalid or extreme parameters."""

    def test_negative_subdivide_cuts(self, router, rpc_client, clean_scene):
        """Test: Subdivide with negative cuts is handled."""
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})
        rpc_client.send_request("mesh.select", {"action": "all"})

        # Negative value
        tools = router.process_llm_tool_call(
            "mesh_subdivide",
            {"number_cuts": -5}
        )

        assert isinstance(tools, list)

        subdivide_tool = next((t for t in tools if t["tool"] == "mesh_subdivide"), None)
        if subdivide_tool:
            # Cuts should be clamped to at least 1
            assert subdivide_tool["params"].get("number_cuts", -5) >= 1

    def test_zero_bevel_width(self, router, rpc_client, clean_scene):
        """Test: Bevel with zero width is handled."""
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})
        rpc_client.send_request("mesh.select", {"action": "all"})

        # Zero width
        tools = router.process_llm_tool_call(
            "mesh_bevel",
            {"width": 0.0}
        )

        assert isinstance(tools, list)

    def test_extremely_large_extrude_depth(self, router, rpc_client, clean_scene):
        """Test: Extrude with huge depth is handled."""
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})
        rpc_client.send_request("mesh.select", {"action": "all"})

        # Extreme depth
        tools = router.process_llm_tool_call(
            "mesh_extrude_region",
            {"depth": 10000.0}
        )

        assert isinstance(tools, list)

        extrude_tool = next((t for t in tools if t["tool"] == "mesh_extrude_region"), None)
        if extrude_tool:
            # Depth may be clamped based on object dimensions
            move = extrude_tool["params"].get("move")
            assert isinstance(move, (list, tuple)) and len(move) == 3


class TestNonMeshObjects:
    """Tests for operations on non-mesh objects."""

    def test_mesh_tool_on_camera(self, router, rpc_client, clean_scene):
        """Test: Mesh tool called with camera as active object."""
        # Create camera
        rpc_client.send_request("scene.create_light_or_camera", {
            "object_type": "CAMERA",
            "location": [0, 0, 5]
        })

        router.invalidate_cache()

        # Try mesh tool on camera
        tools = router.process_llm_tool_call(
            "mesh_subdivide",
            {"number_cuts": 2}
        )

        # Should handle gracefully - may return empty or error
        assert isinstance(tools, list)

    def test_mesh_tool_on_light(self, router, rpc_client, clean_scene):
        """Test: Mesh tool called with light as active object."""
        # Create light
        rpc_client.send_request("scene.create_light_or_camera", {
            "object_type": "LIGHT",
            "location": [0, 0, 3]
        })

        router.invalidate_cache()

        tools = router.process_llm_tool_call(
            "mesh_bevel",
            {"width": 0.1}
        )

        assert isinstance(tools, list)


class TestWorkflowResilience:
    """Tests for workflow execution resilience."""

    def test_tool_sequence_with_intermediate_failure(self, router, rpc_client, clean_scene):
        """Test: Tool sequence where intermediate tool might fail."""
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})
        rpc_client.send_request("mesh.select", {"action": "all"})

        router.invalidate_cache()

        # Get a tool sequence
        tools = router.process_llm_tool_call(
            "mesh_bevel",
            {"width": 0.1, "segments": 2}
        )

        # Execute and track results
        executed = 0
        failed = 0

        for tool in tools:
            tool_name = tool["tool"]
            params = tool["params"]

            # Convert tool name to RPC format
            parts = tool_name.split("_")
            area = parts[0]
            method = "_".join(parts[1:])

            try:
                rpc_client.send_request(f"{area}.{method}", params)
                executed += 1
            except Exception:
                failed += 1

        # Should have executed at least something
        assert executed > 0 or len(tools) == 0

    def test_cache_invalidation_reflects_scene_changes(self, router, rpc_client, clean_scene):
        """Test: Cache invalidation properly reflects scene changes."""
        # Create cube
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        router.invalidate_cache()

        # Get tools for current state
        tools1 = router.process_llm_tool_call(
            "mesh_subdivide",
            {"number_cuts": 2}
        )

        # Change scene significantly
        rpc_client.send_request("modeling.transform_object", {
            "scale": [0.1, 0.1, 5.0]  # Tower-like
        })
        router.invalidate_cache()

        # Get tools again - may be different due to pattern detection
        tools2 = router.process_llm_tool_call(
            "mesh_subdivide",
            {"number_cuts": 2}
        )

        # Both should be valid lists
        assert isinstance(tools1, list)
        assert isinstance(tools2, list)
        assert len(tools1) > 0
        assert len(tools2) > 0


class TestSpecialCharactersInPrompt:
    """Tests for special characters in prompts."""

    def test_prompt_with_unicode_characters(self, router, rpc_client, clean_scene):
        """Test: Prompt with various unicode characters."""
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})
        rpc_client.send_request("mesh.select", {"action": "all"})

        # Prompt with unicode (emoji, accented chars)
        tools = router.process_llm_tool_call(
            "mesh_bevel",
            {"width": 0.1},
            prompt="créer un biseau ✨ с фаской"
        )

        assert isinstance(tools, list)
        assert len(tools) > 0

    def test_prompt_with_special_characters(self, router, rpc_client, clean_scene):
        """Test: Prompt with special characters like quotes."""
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})
        rpc_client.send_request("mesh.select", {"action": "all"})

        # Prompt with quotes and special chars
        tools = router.process_llm_tool_call(
            "mesh_extrude_region",
            {"depth": 0.5},
            prompt='extrude "upward" by 50% & scale'
        )

        assert isinstance(tools, list)
        assert len(tools) > 0
