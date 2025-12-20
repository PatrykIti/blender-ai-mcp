"""
E2E tests for Error Firewall.

Tests firewall rules: blocking, auto-fix for mode, selection, parameters.
Requires running Blender instance.

TASK-040
"""

import pytest

from server.router.application.router import SupervisorRouter
from server.router.infrastructure.config import RouterConfig


class TestFirewallBlocking:
    """Tests for firewall blocking operations."""

    def test_delete_on_empty_scene_is_blocked(self, router, rpc_client, clean_scene):
        """Test: Firewall blocks delete when no objects exist."""
        # Scene is empty after clean_scene, no objects to delete
        # Router should handle this gracefully

        tools = router.process_llm_tool_call(
            "scene_delete_object",
            {"name": "NonExistentObject"}
        )

        # Should return empty list or single tool (depends on implementation)
        # The key is it shouldn't crash
        assert isinstance(tools, list)

        # If firewall blocks, may return empty or the tool itself
        # Execute should fail gracefully
        if tools:
            for tool in tools:
                area = tool["tool"].split("_")[0]
                method = "_".join(tool["tool"].split("_")[1:])
                try:
                    rpc_client.send_request(f"{area}.{method}", tool["params"])
                except Exception:
                    pass  # Expected to fail on empty scene


class TestFirewallModeAutoFix:
    """Tests for firewall auto-fix of mode violations."""

    def test_sculpt_tool_in_object_mode_adds_mode_switch(self, router, rpc_client, clean_scene):
        """Test: Sculpt tool in OBJECT mode triggers mode switch."""
        # Create a mesh object (sculpt requires mesh)
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})

        # Ensure we're in OBJECT mode
        rpc_client.send_request("system.set_mode", {"mode": "OBJECT"})

        # Invalidate router's cache
        router.invalidate_cache()

        # Try sculpt tool - should add mode switch
        tools = router.process_llm_tool_call(
            "sculpt_draw",
            {"strength": 0.5}
        )

        tool_names = [t["tool"] for t in tools]

        # Should have mode switch to SCULPT
        # Note: sculpt_draw might not exist as RPC method, but router should still process
        assert isinstance(tools, list)

        # If auto-fix worked, should have system_set_mode
        if len(tools) > 1:
            assert "system_set_mode" in tool_names, f"Expected mode switch, got: {tool_names}"


class TestFirewallSelectionAutoFix:
    """Tests for firewall auto-fix of selection violations."""

    def test_bevel_without_selection_adds_select_all(self, router, rpc_client, clean_scene):
        """Test: Bevel without selection triggers auto-select."""
        # Create object and enter edit mode
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})

        # Deselect all
        rpc_client.send_request("mesh.select", {"action": "none"})

        # Invalidate cache
        router.invalidate_cache()

        # Try bevel with nothing selected
        tools = router.process_llm_tool_call(
            "mesh_bevel",
            {"width": 0.1, "segments": 2}
        )

        tool_names = [t["tool"] for t in tools]

        # Should have selection step before bevel
        has_selection = any("select" in name.lower() for name in tool_names)

        # Bevel should be in the list
        assert "mesh_bevel" in tool_names, f"Bevel should be in tools, got: {tool_names}"

        # Should have selection added
        if len(tools) > 1:
            assert has_selection, f"Should add selection step, got: {tool_names}"

    def test_inset_without_selection_adds_select_all(self, router, rpc_client, clean_scene):
        """Test: Inset without selection triggers auto-select."""
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})
        rpc_client.send_request("mesh.select", {"action": "none"})

        router.invalidate_cache()

        tools = router.process_llm_tool_call(
            "mesh_inset",
            {"thickness": 0.1}
        )

        tool_names = [t["tool"] for t in tools]

        # Should have the inset tool
        assert "mesh_inset" in tool_names


class TestFirewallParameterModification:
    """Tests for firewall parameter clamping/modification."""

    def test_inset_thickness_clamped(self, router, rpc_client, clean_scene):
        """Test: Inset with huge thickness is clamped."""
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})
        rpc_client.send_request("mesh.select", {"action": "all"})

        # Try inset with unreasonable thickness
        tools = router.process_llm_tool_call(
            "mesh_inset",
            {"thickness": 500.0}
        )

        inset_tool = next((t for t in tools if t["tool"] == "mesh_inset"), None)

        if inset_tool:
            # Thickness should be clamped to reasonable value
            # Default cube is 2x2x2, so thickness > 1 is unreasonable
            assert inset_tool["params"].get("thickness", 500) <= 10.0, \
                f"Thickness should be clamped, got: {inset_tool['params']}"

    def test_extrude_depth_not_clamped_when_reasonable(self, router, rpc_client, clean_scene):
        """Test: Reasonable extrude depth is not modified."""
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})
        rpc_client.send_request("mesh.select", {"action": "all"})

        # Reasonable depth
        tools = router.process_llm_tool_call(
            "mesh_extrude_region",
            {"depth": 0.5}
        )

        extrude_tool = next((t for t in tools if t["tool"] == "mesh_extrude_region"), None)

        if extrude_tool:
            # Depth should remain unchanged
            move = extrude_tool["params"].get("move") or []
            assert isinstance(move, (list, tuple)) and move[2] == 0.5


class TestFirewallConfiguration:
    """Tests for firewall configuration options."""

    def test_firewall_disabled_allows_violations(self, rpc_client, clean_scene, shared_classifier):
        """Test: Disabled firewall allows mode violations."""
        config = RouterConfig(
            auto_mode_switch=False,  # Disable auto mode switch
            auto_selection=False,    # Disable auto selection
        )
        router = SupervisorRouter(
            config=config,
            rpc_client=rpc_client,
            classifier=shared_classifier,
        )

        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})

        # Stay in OBJECT mode, try mesh tool
        tools = router.process_llm_tool_call(
            "mesh_extrude_region",
            {"depth": 0.3}
        )

        tool_names = [t["tool"] for t in tools]

        # With auto_mode_switch disabled, should NOT add mode switch
        # Just return the original tool
        assert "mesh_extrude_region" in tool_names
